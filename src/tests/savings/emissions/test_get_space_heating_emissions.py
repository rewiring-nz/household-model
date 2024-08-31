from constants.utils import PeriodEnum
from savings.emissions.calculate_emissions import (
    get_space_heating_emissions,
)
from unittest.mock import patch
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

    def test_it_returns_weekly_emissions(self, _):
        result = get_space_heating_emissions(mock_household, PeriodEnum.WEEKLY)
        assert result == mock_emissions_daily * 7

    def test_it_returns_yearly_emissions(self, _):
        result = get_space_heating_emissions(mock_household, PeriodEnum.YEARLY)
        assert result == mock_emissions_daily * 365.25

    def test_it_returns_operational_lifetime_emissions(self, _):
        result = get_space_heating_emissions(
            mock_household, PeriodEnum.OPERATIONAL_LIFETIME
        )
        assert result == mock_emissions_daily * 365.25 * 15
