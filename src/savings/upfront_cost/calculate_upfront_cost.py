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


def calculate_upfront_cost(
    current_household: Household, electrified_household: Household
) -> UpfrontCost:
    return UpfrontCost(
        solar=get_solar_upfront_cost(current_household, electrified_household),
        battery=get_battery_upfront_cost(current_household, electrified_household),
        cooktop=get_cooktop_upfront_cost(current_household, electrified_household),
        waterHeating=get_water_heating_upfront_cost(
            current_household, electrified_household
        ),
        spaceHeating=get_space_heating_upfront_cost(
            current_household, electrified_household
        ),
    )
