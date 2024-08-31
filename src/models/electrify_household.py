from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.household import Household
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum


def electrify_household(current_household: Household) -> Household:
    electrified_household = Household(
        **{
            "space_heating": electrify_space_heating(current_household.space_heating),
            "water_heating": electrify_water_heating(current_household.water_heating),
            "cooktop": CooktopEnum.ELECTRIC_RESISTANCE,
            # "vehicles": [
            #     mock_vehicle_petrol,
            #     mock_vehicle_diesel,
            # ],
            # "solar": mock_solar,
            # "battery": mock_battery,
        }
    )
    return electrified_household


def electrify_space_heating(current: SpaceHeatingEnum) -> SpaceHeatingEnum:
    """Converts current space heating to electrified option
    Resistive heaters are swapped for heat pumps as cost savings will be worth it, even if emissions savings are minor.

    Args:
        current (SpaceHeatingEnum): current space heater

    Returns:
        SpaceHeatingEnum: electrified space heater
    """
    return SpaceHeatingEnum.ELECTRIC_HEAT_PUMP


def electrify_water_heating(current: WaterHeatingEnum) -> WaterHeatingEnum:
    """Converts current water heating to electrified option
    Resistive and solar water heaters are NOT swapped for heat pumps.

    Args:
        current (WaterHeatingEnum): current space heater

    Returns:
        WaterHeatingEnum: electrified space heater
    """
    if current not in [WaterHeatingEnum.ELECTRIC_RESISTANCE, WaterHeatingEnum.SOLAR]:
        return WaterHeatingEnum.ELECTRIC_HEAT_PUMP
    return current
