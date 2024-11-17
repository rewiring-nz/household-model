from multiprocessing import Value
from typing import List, Optional

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


def get_energy_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
) -> float:
    """Get energy needs per day for a given machine

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type

    Returns:
        float: machine's energy needs per day
    """
    energy_per_day = machine_stats_map[machine_type]["kwh_per_day"]
    if energy_per_day is None:
        raise ValueError(f"Can not find kwh_per_day value for {machine_type}")
    return energy_per_day


def get_energy_per_period(
    machine: MachineEnum,
    machine_info: MachineInfoMap,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the energy needs of machines in given household over given period

    Args:
        machine (MachineEnum): the machine
        machine_info (MachineInfoMap): info about the machine's energy use per day and its fuel type
        period (PeriodEnum, optional): the period over which to calculate the energy use. Defaults to PeriodEnum.DAILY.

    Returns:
        float: energy needs of operating machine over given period in kWh
    """
    opex_daily = get_energy_per_day(
        machine,
        machine_info,
    )
    return scale_daily_to_period(opex_daily, period)


def get_machine_opex_per_period(
    appliance: MachineEnum,
    appliance_info: MachineInfoMap,
    period: PeriodEnum = PeriodEnum.DAILY,
    energy_per_day: Optional[float] = None,
) -> float:
    """Calculates the opex of appliances

    Calculations over a long period of time (e.g. 15 years) should use this function
    rather than straight multiplying a price over a period
    (e.g. multiplying the yearly price by 15 to get the price over 15 years)
    as this function takes into account economic factors such as inflation

    Args:
        appliance (MachineEnum): the appliance
        appliance_info (MachineInfoMap): info about the machine's energy use per day and its fuel type
        period (PeriodEnum): the period over which to calculate the energy use. Defaults to PeriodEnum.DAILY.
        energy_per_day (float, optional): the energy needs of the machine per day. Will calculate if not provided

    Returns:
        float: cost of operating appliance over given period in NZD to 2dp
    """
    if energy_per_day is None:
        energy_per_day = get_energy_per_day(appliance, appliance_info)

    fuel_type = appliance_info[appliance]["fuel_type"]
    fuel_price = COST_PER_FUEL_KWH_TODAY[fuel_type]
    if fuel_type == FuelTypeEnum.ELECTRICITY:
        fuel_price = fuel_price["volume_rate"]
    opex_per_day = energy_per_day * fuel_price

    opex_per_period = scale_daily_to_period(opex_per_day, period)
    return round(opex_per_period, 2)


def get_other_appliances_energy_per_period(
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the energy of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the energy. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily energy value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: energy of operating other appliances over given period
    """
    return scale_daily_to_period(ENERGY_NEEDS_OTHER_MACHINES_PER_DAY, period)


def get_other_appliances_opex_per_period(
    period: PeriodEnum = PeriodEnum.DAILY,
    energy_per_day: Optional[float] = None,
) -> float:
    """Calculates the opex of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the opex. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily opex value. Defaults to PeriodEnum.DAILY.
        energy_per_day (float, optional): the energy needs of the machine per day. Will calculate if not provided

    Returns:
        float: cost of operating other appliances over given period in NZD to 2dp
    """
    if energy_per_day is None:
        energy_per_day = get_other_appliances_energy_per_period()

    opex_daily = (
        energy_per_day
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
            avg_opex_daily = get_energy_per_day(
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

    petrol = get_energy_per_day(
        VehicleFuelTypeEnum.PETROL,
        VEHICLE_INFO,
    )
    ev = get_energy_per_day(
        VehicleFuelTypeEnum.ELECTRIC,
        VEHICLE_INFO,
    )
    if vehicle_type == VehicleFuelTypeEnum.PLUG_IN_HYBRID:
        # PHEV: Assume 60/40 split between petrol and electric
        return petrol * 0.6 + ev * 0.4
    # HEV: Assume 70/30 split between petrol and electric
    return petrol * 0.7 + ev * 0.3
