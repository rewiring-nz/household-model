from typing import List

from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.household import Household
from openapi_client.models.solar import Solar
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.vehicle import Vehicle
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum

from constants.fuel_stats import (
    COST_PER_FUEL_KWH_TODAY,
    FuelTypeEnum,
)
from constants.machines.machine_info import MachineEnum, MachineInfoMap
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.vehicles import (
    RUCS,
    VEHICLE_INFO,
    VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA,
)
from constants.utils import PeriodEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from params import OPERATIONAL_LIFETIME


FIXED_COSTS_PER_YEAR = {
    FuelTypeEnum.ELECTRICITY: 689,  # on every home
    FuelTypeEnum.NATURAL_GAS: 587,  # Machines!D292
    FuelTypeEnum.LPG: 139,  # Machines!D293
}


def get_opex_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
) -> float:
    """Get opex per day based on machine's energy use per day and opex factor for fuel type

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type

    Returns:
        float: machine's opex in NZD per day, unrounded
    """
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    opex = energy * COST_PER_FUEL_KWH_TODAY[fuel_type]
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
        float: cost of operating appliance over given period in NZD to 2dp
    """
    opex_daily = get_opex_per_day(
        appliance,
        appliance_info,
    )
    return round(_convert_to_period(opex_daily, period), 2)


def get_other_appliance_opex(period: PeriodEnum = PeriodEnum.DAILY) -> float:
    """Calculates the opex of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the opex. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily opex value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: cost of operating other appliances over given period in NZD to 2dp
    """
    opex_daily = (
        ENERGY_NEEDS_OTHER_MACHINES_PER_DAY * COST_PER_FUEL_KWH_TODAY["electricity"]
    )
    return round(_convert_to_period(opex_daily, period), 2)


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

        # Add Road User Charges (RUCs), weighted on kms per year
        rucs_daily = RUCS[vehicle.fuel_type] * vehicle.kms_per_week * 52 / 1000 / 365.25
        weighted_opex_daily += rucs_daily

        # Convert to given period
        opex_period = _convert_to_period(weighted_opex_daily, period)

        # Add to total
        total_opex += opex_period
    return total_opex


def get_fixed_costs(
    household: Household,
    period: PeriodEnum = PeriodEnum.DAILY,
    ignore_lpg_if_ngas_present: bool = False,
) -> float:
    """Calculates the fixed costs you pay per year, for gas and LPG connections.
    Always includes electricity fixed costs, since all households pay this anyway
    for all the other devices we have (we assume the house stays on the grid).

    Args:
        household (Household): TODO
        period (PeriodEnum, optional): _description_. Defaults to PeriodEnum.DAILY.

    Returns:
        float: _description_
    """
    # TODO: unit test, use tests for get_fixed_costs_per_year()
    # These values are all in daily
    grid_connection = FIXED_COSTS_PER_YEAR.get(FuelTypeEnum.ELECTRICITY) / 365.25
    ngas_connection = 0
    lpg_connection = 0
    if (
        household.space_heating == SpaceHeatingEnum.GAS
        or household.water_heating == WaterHeatingEnum.GAS
        or household.cooktop == CooktopEnum.GAS
    ):
        ngas_connection = FIXED_COSTS_PER_YEAR.get(FuelTypeEnum.NATURAL_GAS) / 365.25
    if (
        household.space_heating == SpaceHeatingEnum.LPG
        or household.water_heating == WaterHeatingEnum.LPG
        or household.cooktop == CooktopEnum.LPG
    ):
        lpg_connection = FIXED_COSTS_PER_YEAR.get(FuelTypeEnum.LPG) / 365.25

    if ignore_lpg_if_ngas_present and ngas_connection > 0:
        # Ignore LPG if they've also said they have ngas, because most homes are unlikely to have both an LPG and ngas connection. They are most likely referring to an outdoor BBQ as their "LPG cooktop" or something similar that's uncommonly used and not their usual mode of energy use.
        lpg_connection = 0

    fixed_costs_daily = grid_connection + ngas_connection + lpg_connection
    return _convert_to_period(fixed_costs_daily, period)


def get_solar_savings(solar: Solar, period: PeriodEnum = PeriodEnum.DAILY) -> float:
    # TODO
    # if installing solar
    # substract AVG_SAVINGS_FROM_SOLAR_0_VEHICLES_5KWH or AVG_SAVINGS_FROM_SOLAR_2_VEHICLES_7KWH but dynamic to solar size
    # check if these apply even without battery, and what the impact of the battery is
    savings_daily = 0
    if solar.install_solar:
        savings_daily = 1.5 * solar.size  # dummy value
    return _convert_to_period(savings_daily, period)


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
