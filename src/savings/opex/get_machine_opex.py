from typing import List

from openapi_client.models.vehicle import Vehicle
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum

from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.machine_info import MachineEnum, MachineInfoMap
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.vehicles import (
    VEHICLE_INFO,
    VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA,
)
from constants.utils import PeriodEnum
from params import OPERATIONAL_LIFETIME


def get_opex_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
) -> float:
    """Get opex per day based on machine's energy use per day and opex factor for fuel type

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type

    Returns:
        float: machine's opex in NZD per day to 2dp
    """
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    opex = energy * EMISSIONS_FACTORS[fuel_type]
    return opex


def get_appliance_opex(
    appliance: MachineEnum,
    appliance_info: MachineInfoMap,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the opex from appliance in given household

    Args:
        appliance (MachineEnum): the appliance
        period (PeriodEnum, optional): the period over which to calculate the opex. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily opex value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: NZD emitted from appliance over given period to 2dp
    """
    opex_daily = get_opex_per_day(
        appliance,
        appliance_info,
    )
    return _convert_to_period(opex_daily, period)


def get_other_appliance_opex(period: PeriodEnum = PeriodEnum.DAILY) -> float:
    """Calculates the opex of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the opex. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily opex value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: NZD emitted from other appliances over given period to 2dp
    """
    opex_daily = ENERGY_NEEDS_OTHER_MACHINES_PER_DAY * EMISSIONS_FACTORS["electricity"]
    return _convert_to_period(opex_daily, period)


def get_vehicle_opex(
    vehicles: List[Vehicle], period: PeriodEnum = PeriodEnum.DAILY
) -> float:
    """Calculates the opex of a list of vehicles

    Args:
        vehicles (List[Vehicle]): the list of vehicles
        period (PeriodEnum, optional): the period over which to calculate the opex. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily opex value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: total NZD emitted from vehicles over given period to 2dp
    """
    total_opex = 0
    for vehicle in vehicles:
        if vehicle.fuel_type in [
            VehicleFuelTypeEnum.PLUG_IN_HYBRID,
            VehicleFuelTypeEnum.HYBRID,
        ]:
            avg_opex_daily = _get_hybrid_opex_per_day(vehicle.fuel_type)
        else:
            avg_opex_daily = get_opex_per_day(
                vehicle.fuel_type,
                VEHICLE_INFO,
            )

        # Weight the opex based on how much they use the vehicle compared to average
        weighting_factor = (
            vehicle.kms_per_week * 52 / VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA
        )
        weighted_opex_daily = avg_opex_daily * weighting_factor

        # Convert to given period
        opex_period = _convert_to_period(weighted_opex_daily, period)

        # Add to total
        total_opex += opex_period
    return total_opex


def _get_hybrid_opex_per_day(vehicle_type: VehicleFuelTypeEnum) -> float:
    petrol = get_opex_per_day(
        VehicleFuelTypeEnum.PETROL,
        VEHICLE_INFO,
    )
    ev = get_opex_per_day(
        VehicleFuelTypeEnum.ELECTRIC,
        VEHICLE_INFO,
    )
    if vehicle_type == VehicleFuelTypeEnum.PLUG_IN_HYBRID:
        # PHEV: Assume 60/40 split between petrol and electric
        return petrol * 0.6 + ev * 0.4
    if vehicle_type == VehicleFuelTypeEnum.HYBRID:
        # HEV: Assume 70/30 split between petrol and electric
        return petrol * 0.7 + ev * 0.3


def _convert_to_period(opex_daily: float, period: PeriodEnum) -> float:
    # This might become more complex in future, taking into account macroeconomic effects
    if period == PeriodEnum.DAILY:
        return opex_daily
    if period == PeriodEnum.WEEKLY:
        return opex_daily * 7
    if period == PeriodEnum.YEARLY:
        return opex_daily * 365.25
    if period == PeriodEnum.OPERATIONAL_LIFETIME:
        return opex_daily * 365.25 * OPERATIONAL_LIFETIME
