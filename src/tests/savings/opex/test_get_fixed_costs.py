import pytest
from unittest.mock import Mock, patch

from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.household import Household
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum

from constants.fuel_stats import FuelTypeEnum
from constants.utils import PeriodEnum

from savings.opex.get_fixed_costs import get_fixed_costs

MOCK_FIXED_COSTS = {
    FuelTypeEnum.ELECTRICITY: 400,
    FuelTypeEnum.NATURAL_GAS: 300,
    FuelTypeEnum.LPG: 250,
}


@pytest.fixture
def mock_costs():
    with patch(
        "savings.opex.get_fixed_costs.FIXED_COSTS_PER_YEAR_2024", MOCK_FIXED_COSTS
    ):
        yield


@pytest.fixture
def sample_household():
    return Mock(spec=Household)


class TestGetFixedCosts:
    def test_electricity_only(self, mock_costs, sample_household):
        sample_household.space_heating = None
        sample_household.water_heating = None
        sample_household.cooktop = None

        result = get_fixed_costs(sample_household)
        expected = 400 / 365.25  # Daily electricity cost
        assert result == expected

    def test_with_natural_gas(self, mock_costs, sample_household):
        sample_household.space_heating = SpaceHeatingEnum.GAS
        sample_household.water_heating = None
        sample_household.cooktop = None

        result = get_fixed_costs(sample_household)
        expected = (400 + 300) / 365.25
        assert result == expected

    def test_with_lpg(self, mock_costs, sample_household):
        sample_household.space_heating = None
        sample_household.water_heating = WaterHeatingEnum.LPG
        sample_household.cooktop = None

        result = get_fixed_costs(sample_household)
        expected = (400 + 250) / 365.25
        assert result == expected

    def test_ngas_and_lpg(self, mock_costs, sample_household):
        sample_household.space_heating = SpaceHeatingEnum.GAS
        sample_household.cooktop = CooktopEnum.LPG
        sample_household.water_heating = None

        result = get_fixed_costs(sample_household)
        expected = (400 + 300 + 250) / 365.25
        assert result == pytest.approx(expected)

    def test_ignore_lpg_with_natural_gas(self, mock_costs, sample_household):
        sample_household.space_heating = SpaceHeatingEnum.GAS
        sample_household.cooktop = CooktopEnum.LPG
        sample_household.water_heating = None

        result = get_fixed_costs(sample_household, ignore_lpg_if_ngas_present=True)
        expected = (400 + 300) / 365.25
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        "period,multiplier",
        [
            (PeriodEnum.DAILY, 1),
            (PeriodEnum.WEEKLY, 7),
            (PeriodEnum.YEARLY, 365.25),
            (PeriodEnum.OPERATIONAL_LIFETIME, 365.25 * 15),
        ],
    )
    def test_different_periods(self, mock_costs, sample_household, period, multiplier):
        sample_household.space_heating = None
        sample_household.water_heating = None
        sample_household.cooktop = None
        result = get_fixed_costs(sample_household, period=period)
        daily = 400 / 365.25
        expected = daily * multiplier
        assert result == expected
