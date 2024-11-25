from typing import Optional

from constants.machines.machine_info import AVERAGE_PEOPLE_PER_HOUSEHOLD

# Ratios from AER Electricity and Gas consumption benchmarks for residential customers 2020 study
OCCUPANCY_SCALE = {
    1: 1,
    2: 1.7,
    3: 1.8,
    4: 2.0,
    5: 2.5,
}


def scale_energy_by_occupancy(
    energy_per_average_household: float, occupancy_int: Optional[int] = None
) -> float:
    """Scales energy consumption by occupancy
    Will use the NZ average household size if occupancy not provided.

    Args:
        energy (float): energy consumption in kWh for NZ average household.
        occupancy (Optional[int], optional): Number of people in the household. Defaults to None.

    Returns:
        float: energy consumption scaled proportionally
    """

    if occupancy_int is None:
        return energy_per_average_household

    if occupancy_int == 0:
        raise ValueError("Occupancy must be greater than 0")

    # Maxes out at 5+ people
    if occupancy_int > 5:
        occupancy_int = 5

    multiplier = OCCUPANCY_SCALE[occupancy_int] / AVERAGE_PEOPLE_PER_HOUSEHOLD
    return energy_per_average_household * multiplier
