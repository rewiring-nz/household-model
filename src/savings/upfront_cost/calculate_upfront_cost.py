from savings.upfront_cost.get_machine_upfront_cost import (
    get_solar_upfront_cost,
    get_battery_upfront_cost,
    get_cooktop_upfront_cost,
    get_water_heating_upfront_cost,
    get_space_heating_upfront_cost,
)

from openapi_client.models import (
    Household,
    UpfrontCost,
)


def calculate_upfront_cost(current: Household, electrified: Household) -> UpfrontCost:
    return UpfrontCost(
        solar=get_solar_upfront_cost(current.solar),
        battery=get_battery_upfront_cost(current.battery),
        cooktop=get_cooktop_upfront_cost(current.cooktop, electrified.cooktop),
        waterHeating=get_water_heating_upfront_cost(
            current.water_heating, electrified.water_heating
        ),
        spaceHeating=get_space_heating_upfront_cost(
            current.space_heating,
            electrified.space_heating,
            electrified.location,  # Location won't change so just pick either
        ),
    )
