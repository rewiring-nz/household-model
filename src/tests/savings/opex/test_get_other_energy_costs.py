import pytest
from constants.fuel_stats import FuelTypeEnum
from constants.utils import PeriodEnum
from savings.opex.get_other_energy_costs import get_other_energy_costs


def test_it_merges_correctly():
    e_consmpt = {
        FuelTypeEnum.NATURAL_GAS: 2000.0,
        FuelTypeEnum.PETROL: 6000.0,
        FuelTypeEnum.DIESEL: 2500.0,
    }
    result = get_other_energy_costs(e_consmpt, PeriodEnum.DAILY)
    expected = 2000.0 * 0.118 + 6000.0 * 0.28884 + 2500.0 * 0.19679
    assert result == expected


@pytest.mark.parametrize(
    "period,expected",
    [
        (PeriodEnum.DAILY, 500.0 * 0.118 + 1000.0 * 0.28884),
        (PeriodEnum.WEEKLY, 500.0 * 0.118 + 1000.0 * 0.28884),
        (PeriodEnum.YEARLY, 500.0 * 0.118 + 1000.0 * 0.28884),
        (PeriodEnum.OPERATIONAL_LIFETIME, 500.0 * 0.13602 + 1000.0 * 0.35125),
    ],
)
def test_it_uses_correct_pricing(period, expected):
    e_consmpt = {
        FuelTypeEnum.NATURAL_GAS: 500.0,
        FuelTypeEnum.PETROL: 1000.0,
    }
    assert get_other_energy_costs(e_consmpt, period) == expected
