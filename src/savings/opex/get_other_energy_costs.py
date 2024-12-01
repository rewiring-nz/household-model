from constants.fuel_stats import COST_PER_FUEL_KWH_TODAY
from savings.energy.get_other_energy_consumption import (
    OtherEnergyConsumption,
)


def get_other_energy_costs(other_e_consumption: OtherEnergyConsumption) -> float:
    total = 0
    for fuel_type, energy in other_e_consumption.items():
        # TODO: use average 15 year costs if period is lifetime
        total += energy * COST_PER_FUEL_KWH_TODAY[fuel_type]
    return total
