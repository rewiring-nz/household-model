from random import randint
from constants.machines.cooktop import COOKTOP_UPFRONT_COST
from constants.machines.water_heating import WATER_HEATING_UPFRONT_COST
from openapi_client.models.battery import Battery
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.household import Household
from openapi_client.models.solar import Solar
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum


def get_solar_upfront_cost(current: Solar, electrified: Solar) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)


def get_battery_upfront_cost(current: Battery, electrified: Battery) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)


def get_cooktop_upfront_cost(current: CooktopEnum, electrified: CooktopEnum) -> float:
    if current == electrified or current == CooktopEnum.DONT_KNOW:
        return 0
    cost_info = COOKTOP_UPFRONT_COST.get(electrified)
    return round(sum(cost_info.values()), 2)


def get_water_heating_upfront_cost(
    current: WaterHeatingEnum, electrified: WaterHeatingEnum
) -> float:
    if current == electrified or current == WaterHeatingEnum.DONT_KNOW:
        return 0
    cost_info = WATER_HEATING_UPFRONT_COST.get(electrified)
    return round(sum(cost_info.values()), 2)


def get_space_heating_upfront_cost(
    current: SpaceHeatingEnum, electrified: SpaceHeatingEnum
) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)
