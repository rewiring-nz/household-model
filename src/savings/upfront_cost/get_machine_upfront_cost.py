from random import randint
from openapi_client.models.household import Household


def get_solar_upfront_cost(
    current_household: Household, electrified_household: Household
) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)


def get_battery_upfront_cost(
    current_household: Household, electrified_household: Household
) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)


def get_cooktop_upfront_cost(
    current_household: Household, electrified_household: Household
) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)


def get_water_heating_upfront_cost(
    current_household: Household, electrified_household: Household
) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)


def get_space_heating_upfront_cost(
    current_household: Household, electrified_household: Household
) -> float:
    cost = randint(0, 10000) + randint(0, 100) / 100
    return round(cost, 2)
