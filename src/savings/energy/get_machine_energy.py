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


from constants.utils import PeriodEnum
from openapi_client.models.household import Household

from dataclasses import dataclass


@dataclass
class EnergyNeeds:
    appliances: int
    vehicles: int


def get_total_energy_needs(household: Household, period: PeriodEnum) -> EnergyNeeds:
    e_needs_appliances = 10  # includes fixed costs
    e_needs_vehicles = 20  # includes RUCs
    return EnergyNeeds(appliances=e_needs_appliances, vehicles=e_needs_vehicles)


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


def _get_hybrid_energy_per_day(vehicle_type: VehicleFuelTypeEnum) -> float:
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
