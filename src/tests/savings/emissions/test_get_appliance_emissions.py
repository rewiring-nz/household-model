from constants.utils import PeriodEnum
from savings.emissions.get_appliance_emissions import (
    get_appliance_emissions,
    _convert_to_period,
)
from unittest.mock import patch
from tests.mocks import mock_household
from openapi_client.models import SpaceHeatingEnum
from constants.machines.space_heating import SPACE_HEATING_INFO


mock_emissions_daily = 12.3


@patch(
    "savings.emissions.get_appliance_emissions._convert_to_period",
    return_value=mock_emissions_daily,
)
@patch(
    "savings.emissions.get_appliance_emissions.get_emissions_per_day",
    return_value=mock_emissions_daily,
)
class TestGetApplianceEmissions:
    def test_it_calls_get_emissions_per_day_correctly(
        self, mock_get_emissions_per_day, mock_convert_to_period
    ):
        get_appliance_emissions(mock_household, SPACE_HEATING_INFO)
        mock_get_emissions_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO
        )
        mock_convert_to_period.assert_called_once_with(
            mock_emissions_daily, PeriodEnum.DAILY
        )


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
