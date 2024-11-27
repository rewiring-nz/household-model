from typing import Optional


# See Methodology for source & calculations
OCCUPANCY_MULTIPLIER = {
    1: 0.56,
    2: 0.90,
    3: 1.03,
    4: 1.07,
    5: 1.37,  # calculated for 5+
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

    return energy_per_average_household * OCCUPANCY_MULTIPLIER[occupancy_int]
