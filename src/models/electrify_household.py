from constants.machines.machine_info import MachineEnum
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


def should_electrify(current: MachineEnum, electrify_func) -> bool:
    """Determines if the machine should be electrified

    Args:
        current (MachineEnum): the current machine type
        electrify_func (function): a function that returns an electrified version of the current machine

    Returns:
        bool: whether the machine should be electrified or not
    """
    electrified = electrify_func(current)
    return electrified != current


def should_install(current: Solar | Battery) -> bool:
    """Determines if the item should be installed

    Args:
        current (Solar | Battery): the item info including the user's preference on whether to install

    Returns:
        bool: whether the item should be installed or not
    """
    if isinstance(current, Solar):
        # Install solar if they don't have solar & want to install solar
        return not current.has_solar and current.install_solar

    if isinstance(current, Battery):
        # Install battery if they don't have battery & want to install battery
        return not current.has_battery and current.install_battery


def electrify_space_heating(current: SpaceHeatingEnum) -> SpaceHeatingEnum:
    """Converts current space heating to electrified option
    Resistive heaters are swapped for heat pumps as cost savings will be worth it, even if emissions savings are minor.

    Args:
        current (SpaceHeatingEnum): current space heater

    Returns:
        SpaceHeatingEnum: electrified space heater
    """
    # Doesn't actually need current heating, because it will always replace with heat pump.
    # If we move away from only recommending heat pumps, we will need to update the scaling factor in calculations (e.g. the hard-coded use of N_HEAT_PUMPS_NEEDED_PER_LOCATION rather than it being dynamic to the heater type that is being installed)
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
    if current.switch_to_ev:
        return current.copy(
            update={"fuel_type": VehicleFuelTypeEnum.ELECTRIC, "switch_to_ev": None}
        )
    return current


def install_solar(current: Solar) -> Solar:
    """Gets solar if user wants"""
    if should_install(current):
        return current.copy(update={"has_solar": True, "install_solar": None})
    return current


def install_battery(current: Battery) -> Battery:
    """Gets battery if user wants"""
    if should_install(current):
        return current.copy(update={"has_battery": True, "install_battery": None})
    return current
