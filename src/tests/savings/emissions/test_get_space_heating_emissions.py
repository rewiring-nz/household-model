import pandas as pd
import pytest
from constants.utils import PeriodEnum
from savings.emissions.calculate_emissions import (
    get_space_heating_emissions,
    get_space_heating_emissions_savings,
)
from unittest.mock import patch
from tests.process_test_data import get_test_data
from tests.mocks import mock_household
from openapi_client.models import SpaceHeatingEnum
from constants.machines.space_heating import SPACE_HEATING_STATS


mock_emissions_daily = 12.3


@patch(
    "savings.emissions.get_space_heating_emissions.get_emissions_per_day",
    return_value=mock_emissions_daily,
)
class TestGetSpaceHeatingEmissions:
    def test_it_calls_get_emissions_per_day_correctly(self, mock_get_emissions_per_day):
        get_space_heating_emissions(mock_household)
        mock_get_emissions_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_STATS
        )

    def test_it_returns_daily_emissions_by_default(self, _):
        result = get_space_heating_emissions(mock_household)
        assert result == mock_emissions_daily

    def test_it_returns_daily_emissions_if_specified(self, _):
        result = get_space_heating_emissions(mock_household, PeriodEnum.DAILY)
        assert result == mock_emissions_daily

    def test_it_returns_yearly_emissions(self, _):
        result = get_space_heating_emissions(mock_household, PeriodEnum.YEARLY)
        assert result == mock_emissions_daily * 365.25

    def test_it_returns_operational_lifetime_emissions(self, _):
        result = get_space_heating_emissions(
            mock_household, PeriodEnum.OPERATIONAL_LIFETIME
        )
        assert result == mock_emissions_daily * 365.25 * 15


# Assumes electricity emission factor of 0.098 (not 100% renewable grid)


class TestSpaceHeating:
    base_household = get_test_data("tests/base_household.csv")

    def test_it_calculates_savings_for_simple_central_ff_system(self):
        emissions_before, savings = get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating_Central diesel heating": 1,
                }
            )
        )
        expected_emissions_before = 12.8 * 0.253
        assert emissions_before == expected_emissions_before
        expected_savings = expected_emissions_before - (2.7 / 2 * 0.098) * 2
        assert savings == expected_savings

    def test_it_calculates_savings_for_multiple_individual_systems(self):
        expected_emissions = 14.3 * 0.025 * 2
        assert get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating_Wood fireplace(s)": 1,
                    "Home heating number_Wood fireplace": 2,
                }
            )
        ) == (expected_emissions, (expected_emissions - (2.7 / 2 * 0.098 * 2 * 2)))

    def test_it_handles_number_col_only(self):
        assert get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    # Recognises this, even if they didn't select it in the boolean options (or there wasn't one available)
                    "Home heating number_Diesel heater": 3,
                }
            )
        ) == (
            (12.8 / 4 * 0.253 * 3),
            (12.8 / 4 * 0.253 * 3) - (2.7 / 2 * 0.098 * 3 * 0.5),  # 8.9214
        )

    def test_it_accurately_calculates_for_existing_resistive_electric_heaters(self):
        emissions, savings = get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 3,
                }
            )
        )
        expected_emissions = 9.3 / 8 * 0.098 * 3
        assert emissions == expected_emissions
        expected_savings = expected_emissions - (
            2.7 / 2 * 0.098 * 0.25 * 3
        )  # replacement ratio is 3 resistive : 1 heat pump
        assert savings == expected_savings

    def test_it_does_not_replace_central_heat_pump(self):
        # Central heat pump is the only thing that doesn't need to get replaced
        assert get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating_Heat pump central system (one indoor unit for the entire home)": 1,
                }
            )
        ) == (
            (2.7 * 0.098),
            0,
        )

    def test_it_does_not_replace_underfloor_electric(self):
        assert get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating_Underfloor electric heating": 1,
                }
            )
        ) == (9.3 * 0.098, 0)

    def test_it_accurately_calculates_if_they_already_have_the_best_option(self):
        assert get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating_Heat pump split system (an individual unit in a room(s))": 2,
                }
            )
        ) == ((2.7 / 2 * 0.098 * 2), 0)

    def test_it_calculates_savings_for_all_combined(self):
        expected_emissions_before = (
            (11.6 / 2 * 0.217)  # gas/lpg fireplace
            + (14.3 * 0.025 * 2)  # 2 x wood
            + (12.8 / 4 * 0.253 * 3)  # 3 x diesel
            + (11.6 / 4 * 0.217)  # small gas
            + (9.3 / 8 * 0.098)  # electric resistace
        )
        result = get_space_heating_emissions_savings(
            pd.Series(
                {
                    **self.base_household,
                    "Home heating number_Gas or LPG fireplace": 1,
                    "Home heating_Wood fireplace(s)": 1,  # doesn't count this because it's accounted for in the numbers col below
                    "Home heating number_Wood fireplace": 2,
                    "Home heating number_Diesel heater": 3,
                    "Home heating_Gas small heater(s) (not LPG)": 1,  # gets coalesced into "Home heating number_Gas or LPG small heater" which has ratio of 3.95
                    # electric is also switched over
                    "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 1,
                }
            )
        )
        # 7.5 heat pumps needed
        expected_emissions_after = (
            2.7 / 2 * 0.098 * ((1) + (2 * 2) + (3 * 0.5) + (0.5) + (0.25))
        )
        expected_savings = expected_emissions_before - expected_emissions_after
        assert round(result[0], 6) == round(expected_emissions_before, 6)
        assert round(result[1], 6) == round(expected_savings, 6)
