from openapi_client.models import (
    SpaceHeatingEnum,
)

from constants.fuel_stats import EMISSIONS_FACTORS
from typing import Optional

from params import HOUSEHOLD_ENERGY_USE


def get_emissions_per_day(
    machine_type: SpaceHeatingEnum,
    machine_stats_map: dict,
) -> float:
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    emissions = energy * EMISSIONS_FACTORS[fuel_type]  # kgCO2e/kWh
    return emissions


def get_emissions_per_day_old(
    machine_type: str,
    energy_per_day_map: dict,
    type_to_fuel_map: dict,
    household_energy_use: Optional[float] = HOUSEHOLD_ENERGY_USE,
) -> float:
    energy = energy_per_day_map[machine_type] * household_energy_use  # kWh/day
    fuel_type = type_to_fuel_map[machine_type]
    emissions = energy * EMISSIONS_FACTORS[fuel_type]  # kgCO2e/kWh
    return emissions
