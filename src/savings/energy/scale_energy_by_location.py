from typing import Optional

from constants.machines.space_heating import SPACE_HEATING_ENERGY_LOCATION_MULTIPLIER
from openapi_client.models.location_enum import LocationEnum
from constants.machines.machine_info import MachineEnum
from openapi_client.models.space_heating_enum import SpaceHeatingEnum


def scale_energy_by_location(
    machine_type: MachineEnum,
    energy_per_average_household: float,
    location: Optional[LocationEnum] = None,
) -> float:
    """Scales energy consumption by location

    Args:
        energy (float): energy consumption in kWh for NZ average household
        location (LocationEnum, optional): The location of the machine

    Returns:
        float: energy consumption scaled according to region's energy needs
    """

    multiplier = 1

    if type(machine_type) == SpaceHeatingEnum:
        multiplier = (
            1
            if location is None
            else SPACE_HEATING_ENERGY_LOCATION_MULTIPLIER.get(location, 1)
        )
    return energy_per_average_household * multiplier
