from typing import Optional

from constants.machines.machine_info import AVERAGE_PEOPLE_PER_HOUSEHOLD


def scale_energy_by_occupancy(
    energy_per_average_household: float, occupancy_int: Optional[int] = None
) -> float:
    """Scales energy consumption by occupancy.
    Will use the NZ average household size if occupancy not provided.

    Args:
        energy (float): energy consumption in kWh for NZ average household.
        occupancy (Optional[int], optional): Number of people in the household. Defaults to None.

    Returns:
        float: energy consumption scaled proportionally
    """

    occupancy_float = float(
        occupancy_int if occupancy_int is not None else AVERAGE_PEOPLE_PER_HOUSEHOLD
    )

    multiplier = occupancy_float / AVERAGE_PEOPLE_PER_HOUSEHOLD
    return energy_per_average_household * multiplier
