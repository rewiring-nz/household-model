from constants.utils import PeriodEnum
from openapi_client.models.household import Household

from dataclasses import dataclass


@dataclass
class EnergyNeeds:
    appliances: int
    vehicles: int


def get_total_energy_needs(household: Household, period: PeriodEnum) -> EnergyNeeds:
    e_needs_appliances = 10  # includes fixed costs
    e_needs_vehicles = 20  # includes RUCs
    return EnergyNeeds(appliances=e_needs_appliances, vehicles=e_needs_vehicles)
