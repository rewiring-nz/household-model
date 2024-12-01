from constants.fuel_stats import FuelTypeEnum
from savings.opex.get_other_energy_costs import get_other_energy_costs


def test_it_merges_correctly():
    e_consmpt = {
        FuelTypeEnum.NATURAL_GAS: 2000.0,
        FuelTypeEnum.PETROL: 6000.0,
        FuelTypeEnum.DIESEL: 2500.0,
    }
    result = get_other_energy_costs(e_consmpt)
    expected = 2000.0 * 0.118 + 6000.0 * 0.28884 + 2500.0 * 0.19679
    assert result == expected
