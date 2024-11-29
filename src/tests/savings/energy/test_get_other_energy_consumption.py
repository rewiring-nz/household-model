from constants.fuel_stats import FuelTypeEnum
from savings.energy.get_other_energy_consumption import get_other_energy_consumption


def test_it_merges_correctly():
    e_needs = {
        "appliances": {
            FuelTypeEnum.ELECTRICITY: 5000.0,
            FuelTypeEnum.NATURAL_GAS: 2000.0,
        },
        "vehicles": {
            FuelTypeEnum.ELECTRICITY: 3000.0,
            FuelTypeEnum.PETROL: 6000.0,
            FuelTypeEnum.DIESEL: 2500.0,
        },
        "other_appliances": {FuelTypeEnum.ELECTRICITY: 14.0},
    }
    result = get_other_energy_consumption(e_needs)
    expected = {
        FuelTypeEnum.NATURAL_GAS: 2000.0,
        FuelTypeEnum.PETROL: 6000.0,
        FuelTypeEnum.DIESEL: 2500.0,
    }
    assert result == expected
