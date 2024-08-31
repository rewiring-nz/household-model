from constants.machines.vehicles import VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA
from openapi_client.models import (
    Battery,
    CooktopEnum,
    Household,
    Solar,
    SpaceHeatingEnum,
    Vehicle,
    VehicleFuelTypeEnum,
    WaterHeatingEnum,
)


def electrify_household(current_household: Household) -> Household:
    electrified_household = Household(
        **{
            "location": current_household.location,
            "occupancy": current_household.occupancy,
            "space_heating": electrify_space_heating(current_household.space_heating),
            "water_heating": electrify_water_heating(current_household.water_heating),
            "cooktop": electrify_cooktop(current_household.cooktop),
            "vehicles": [electrify_vehicle(v) for v in current_household.vehicles],
            "solar": install_solar(current_household.solar),
            "battery": install_battery(current_household.battery),
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
    # Doesn't actually need current heating, because it will always replace with heat pump.
    return SpaceHeatingEnum.ELECTRIC_HEAT_PUMP


def electrify_water_heating(current: WaterHeatingEnum) -> WaterHeatingEnum:
    """Converts current water heating to electrified option
    Resistive and solar water heaters are NOT swapped for heat pumps.

    Args:
        current (WaterHeatingEnum): current water heater

    Returns:
        WaterHeatingEnum: electrified water heater
    """
    if current in [
        WaterHeatingEnum.ELECTRIC_RESISTANCE,
        WaterHeatingEnum.SOLAR,
        WaterHeatingEnum.ELECTRIC_HEAT_PUMP,
    ]:
        return current
    return WaterHeatingEnum.ELECTRIC_HEAT_PUMP


def electrify_cooktop(current: CooktopEnum) -> CooktopEnum:
    """Converts current cooktop to electrified option
    Resistive cooktops are NOT swapped for induction.

    Args:
        current (CooktopEnum): current cooktop

    Returns:
        CooktopEnum: electrified cooktop
    """
    if current in [CooktopEnum.ELECTRIC_RESISTANCE, CooktopEnum.ELECTRIC_INDUCTION]:
        return current
    return CooktopEnum.ELECTRIC_INDUCTION


def electrify_vehicle(current: Vehicle) -> Vehicle:
    """Converts current vehicle to EV depending on user preference

    Args:
        current (Vehicle): current vehicle

    Returns:
        Vehicle: electrified vehicle
    """
    vehicle = current.copy(
        update={
            "kms_per_week": (
                # average per capita is  212 km/week
                # TODO: use average per vehicle, not capita
                round(VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA / 52)
                if current.kms_per_week is None
                else current.kms_per_week
            )
        }
    )
    if vehicle.switch_to_ev:
        return vehicle.copy(
            update={"fuel_type": VehicleFuelTypeEnum.ELECTRIC, "switch_to_ev": None}
        )
    return vehicle


def install_solar(current: Solar) -> Solar:
    """Gets solar if user wants"""
    if current.install_solar:
        return current.copy(update={"has_solar": True, "install_solar": None})
    return current


def install_battery(current: Battery) -> Battery:
    """Gets battery if user wants"""
    if current.install_battery:
        return current.copy(update={"has_battery": True, "install_battery": None})
    return current
