from openapi_client.models.solar import Solar


def get_solar_savings(solar: Solar) -> float:
    # TODO
    # if installing solar
    # substract AVG_SAVINGS_FROM_SOLAR_0_VEHICLES_5KWH or AVG_SAVINGS_FROM_SOLAR_2_VEHICLES_7KWH but dynamic to solar size
    # check if these apply even without battery, and what the impact of the battery is
    return 0
