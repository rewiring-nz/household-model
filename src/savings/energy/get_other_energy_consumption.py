from typing import Dict
from constants.fuel_stats import FuelTypeEnum
from savings.energy.get_machine_energy import MachineEnergyNeeds

OtherEnergyConsumption = Dict[FuelTypeEnum, float]


def get_other_energy_consumption(
    energy_needs: MachineEnergyNeeds,
) -> OtherEnergyConsumption:
    """Gets total energy consumption for fuel types other than electricity
    across all machine categories

    Args:
        energy_needs (MachineEnergyNeeds): energy needs per machine category by fuel type

    Returns:
        OtherEnergyConsumption: energy needs per fuel type except electricity
    """
    result = {}
    for category_needs in energy_needs.values():
        for fuel_type, consumption in category_needs.items():
            if fuel_type != FuelTypeEnum.ELECTRICITY:
                result[fuel_type] = result.get(fuel_type, 0) + consumption
    return result
