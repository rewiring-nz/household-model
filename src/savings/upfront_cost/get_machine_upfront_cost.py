from typing import Optional
from constants.machines.cooktop import COOKTOP_UPFRONT_COST
from constants.machines.space_heating import (
    N_HEAT_PUMPS_NEEDED_PER_LOCATION,
    SPACE_HEATING_UPFRONT_COST,
)
from constants.machines.water_heating import WATER_HEATING_UPFRONT_COST
from models.electrify_household import should_install
from openapi_client.models.battery import Battery
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum

# Takes into account the inverter
SOLAR_COST_PER_KW = 20500 / 9  # $2277.78

BATTERY_COST_PER_KWH = 1000


def get_solar_upfront_cost(current: Solar) -> float:
    if should_install(current):
        return round(SOLAR_COST_PER_KW * current.size, 2)
    return 0


def get_battery_upfront_cost(current: Battery) -> float:
    if should_install(current):
        return round(BATTERY_COST_PER_KWH * current.capacity, 2)
    return 0


def get_cooktop_upfront_cost(current: CooktopEnum, electrified: CooktopEnum) -> float:
    if current == electrified:
        return 0
    cost_info = COOKTOP_UPFRONT_COST.get(electrified)
    return round(sum(cost_info.values()), 2)


def get_water_heating_upfront_cost(
    current: WaterHeatingEnum, electrified: WaterHeatingEnum
) -> float:
    if current == electrified:
        return 0
    cost_info = WATER_HEATING_UPFRONT_COST.get(electrified)
    return round(sum(cost_info.values()), 2)


def get_space_heating_upfront_cost(
    current: SpaceHeatingEnum,
    electrified: SpaceHeatingEnum,
    location: Optional[LocationEnum] = None,
) -> float:
    if current == electrified:
        return 0
    cost_info = SPACE_HEATING_UPFRONT_COST.get(electrified)
    cost_per_heater = sum(cost_info.values())

    # Scale number of heat pumps required depending on location, default is 2
    # N.B. If we move away from only recommending heat pumps for space heater electrification, we'll need to update this because this is only referring to the estimated number of heat pumps required, not any generic heater.
    n_heaters = N_HEAT_PUMPS_NEEDED_PER_LOCATION.get(location, 2)

    total_cost = cost_per_heater * n_heaters
    return round(total_cost, 2)
