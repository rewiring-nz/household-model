from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.utils import PeriodEnum
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from savings.emissions.get_appliance_emissions import (
    get_appliance_emissions,
    _convert_to_period,
    get_other_appliance_emissions,
)
from unittest.mock import patch
from tests.mocks import mock_household
from openapi_client.models import SpaceHeatingEnum
from constants.machines.space_heating import SPACE_HEATING_INFO


mock_emissions_daily = 12.3
mock_emissions_weekly = 12.3 * 7


@patch(
    "savings.emissions.get_appliance_emissions._convert_to_period",
    return_value=mock_emissions_weekly,
)
@patch(
    "savings.emissions.get_appliance_emissions.get_emissions_per_day",
    return_value=mock_emissions_daily,
)
class TestGetApplianceEmissions:
    def test_it_calls_get_emissions_for_space_heating_correctly(
        self, mock_get_emissions_per_day, _
    ):
        get_appliance_emissions(mock_household.space_heating, SPACE_HEATING_INFO)
        mock_get_emissions_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO
        )

    def test_it_calls_get_emissions_for_water_heating_correctly(
        self, mock_get_emissions_per_day, _
    ):
        get_appliance_emissions(mock_household.water_heating, WATER_HEATING_INFO)
        mock_get_emissions_per_day.assert_called_once_with(
            WaterHeatingEnum.GAS, WATER_HEATING_INFO
        )

    def test_it_calls_get_emissions_for_cooktop_correctly(
        self, mock_get_emissions_per_day, _
    ):
        get_appliance_emissions(mock_household.cooktop, COOKTOP_INFO)
        mock_get_emissions_per_day.assert_called_once_with(
            CooktopEnum.ELECTRIC_RESISTANCE, COOKTOP_INFO
        )

    def test_it_calls_convert_to_period_correctly(self, _, mock_convert_to_period):
        get_appliance_emissions(mock_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY)
        mock_convert_to_period.assert_called_once_with(
            mock_emissions_daily, PeriodEnum.WEEKLY
        )

    def test_it_calls_convert_to_period_correctly_with_default(
        self, _, mock_convert_to_period
    ):
        get_appliance_emissions(mock_household.cooktop, COOKTOP_INFO)
        mock_convert_to_period.assert_called_once_with(
            mock_emissions_daily, PeriodEnum.DAILY
        )

    def test_it_returns_emissions_per_period(self, _, __):
        result = get_appliance_emissions(
            mock_household.space_heating, SPACE_HEATING_INFO
        )
        assert result == mock_emissions_weekly


@patch(
    "savings.emissions.get_appliance_emissions._convert_to_period",
    return_value=mock_emissions_weekly,
)
class TestGetOtherApplianceEmissions:
    emissions_daily = (0.34 + 4.48 + 3.06) * 0.098

    def test_it_calls_convert_to_period_correctly(self, mock_convert_to_period):
        get_other_appliance_emissions(PeriodEnum.WEEKLY)
        mock_convert_to_period.assert_called_once_with(
            self.emissions_daily, PeriodEnum.WEEKLY
        )

    def test_it_calls_convert_to_period_correctly_with_default(
        self, mock_convert_to_period
    ):
        get_other_appliance_emissions()
        mock_convert_to_period.assert_called_once_with(
            self.emissions_daily, PeriodEnum.DAILY
        )

    def test_it_returns_emissions_per_period(self, _):
        result = get_other_appliance_emissions()
        assert result == mock_emissions_weekly


class TestConvertToPeriod:
    def test_it_returns_daily_emissions(self):
        result = _convert_to_period(mock_emissions_daily, PeriodEnum.DAILY)
        assert result == mock_emissions_daily

    def test_it_returns_weekly_emissions(self):
        result = _convert_to_period(mock_emissions_daily, PeriodEnum.WEEKLY)
        assert result == mock_emissions_daily * 7

    def test_it_returns_yearly_emissions(self):
        result = _convert_to_period(mock_emissions_daily, PeriodEnum.YEARLY)
        assert result == mock_emissions_daily * 365.25

    def test_it_returns_operational_lifetime_emissions(self):
        result = _convert_to_period(
            mock_emissions_daily, PeriodEnum.OPERATIONAL_LIFETIME
        )
        assert result == mock_emissions_daily * 365.25 * 15
