from typing import List

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
    VEHICLE_AVG_KMS_PER_WEEK,
    VEHICLE_INFO,
)
from constants.utils import DAYS_PER_YEAR, WEEKS_PER_YEAR, PeriodEnum
from utils.scale_daily_to_period import scale_daily_to_period


def get_opex_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
) -> float:
    """Get opex per day for a given machine

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type

    Returns:
        float: machine's opex in NZD per day, unrounded
    """
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    fuel_price = COST_PER_FUEL_KWH_TODAY[fuel_type]
    if fuel_type == FuelTypeEnum.ELECTRICITY:
        fuel_price = fuel_price["volume_rate"]
    opex = energy * fuel_price
    return opex


def get_appliance_energy(
    appliance: MachineEnum,
    appliance_info: MachineInfoMap,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the energy needs of appliances in given household

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
    return round(scale_daily_to_period(opex_daily, period), 2)


def get_other_appliances_opex(period: PeriodEnum = PeriodEnum.DAILY) -> float:
    """Calculates the opex of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the opex. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily opex value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: cost of operating other appliances over given period in NZD to 2dp
    """
    opex_daily = (
        ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
        * COST_PER_FUEL_KWH_TODAY[FuelTypeEnum.ELECTRICITY]["volume_rate"]
    )
    return round(scale_daily_to_period(opex_daily, period), 2)


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
        weighting_factor = vehicle.kms_per_week / VEHICLE_AVG_KMS_PER_WEEK
        weighted_opex_daily = avg_opex_daily * weighting_factor

        # Add Road User Charges (RUCs), weighted on kms per year
        rucs_daily = (
            RUCS[vehicle.fuel_type]  # $/yr/1000km
            * vehicle.kms_per_week  # km/wk
            * WEEKS_PER_YEAR  # wk/yr
            / 1000
            / DAYS_PER_YEAR  # days/yr
        )
        weighted_opex_daily += rucs_daily

        # Convert to given period
        opex_period = scale_daily_to_period(weighted_opex_daily, period)

        # Add to total
        total_opex += opex_period
    return total_opex


def _get_hybrid_opex_per_day(vehicle_type: VehicleFuelTypeEnum) -> float:
    if not isinstance(vehicle_type, VehicleFuelTypeEnum):
        raise TypeError(
            f"vehicle_type must be VehicleFuelTypeEnum, got {type(vehicle_type)}"
        )

    if vehicle_type not in (
        VehicleFuelTypeEnum.PLUG_IN_HYBRID,
        VehicleFuelTypeEnum.HYBRID,
    ):
        raise ValueError(
            f"vehicle_type must be PLUG_IN_HYBRID or HYBRID, got {vehicle_type.value}"
        )

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
    # HEV: Assume 70/30 split between petrol and electric
    return petrol * 0.7 + ev * 0.3
