from dataclasses import dataclass
from typing import Dict, List, Optional

from constants.fuel_stats import FuelTypeEnum
from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.space_heating import SPACE_HEATING_INFO
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.machines.machine_info import MachineEnum, MachineInfoMap
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.vehicles import (
    VEHICLE_AVG_KMS_PER_WEEK,
    VEHICLE_INFO,
)
from constants.utils import PeriodEnum
from savings.energy.scale_energy_by_occupancy import scale_energy_by_occupancy
from utils.scale_daily_to_period import scale_daily_to_period

from openapi_client.models import Vehicle, VehicleFuelTypeEnum, Household


@dataclass
class MachineEnergyNeeds:
    appliances: Dict[FuelTypeEnum, float]
    vehicles: Dict[FuelTypeEnum, float]
    other_appliances: Dict[FuelTypeEnum, float]


def get_total_energy_needs(
    household: Household, period: PeriodEnum
) -> MachineEnergyNeeds:
    appliance_energy = get_total_appliance_energy(household, period)
    vehicle_energy = get_vehicle_energy(household.vehicles, period)
    other_energy = get_other_appliances_energy_per_period(household.occupancy, period)
    return MachineEnergyNeeds(
        appliances=appliance_energy,
        vehicles=vehicle_energy,
        other_appliances=other_energy,
    )


def get_energy_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
    occupancy: Optional[int] = None,
) -> Dict[FuelTypeEnum, float]:
    """Get energy needs per day for a given machine

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type
        occupancy (int, optional): The number of people in the household.

    Returns:
        Dict[FuelTypeEnum, float]: machine's energy needs per day per fuel type
    """
    machine_infos = machine_stats_map[machine_type]
    if type(machine_stats_map[machine_type]) != list:
        machine_infos = [machine_infos]

    e_fuel_type = {}

    for machine_info in machine_infos:
        e_daily = machine_info["kwh_per_day"]
        if e_daily is None:
            raise ValueError(f"Can not find kwh_per_day value for {machine_type}")

        fuel_type = machine_info["fuel_type"]
        if fuel_type is None:
            raise ValueError(f"Can not find fuel type value for {machine_type}")

        e_daily_scaled = scale_energy_by_occupancy(e_daily, occupancy)
        e_fuel_type[fuel_type] = e_daily_scaled

    return e_fuel_type


def get_energy_per_period(
    machine: MachineEnum,
    machine_info: MachineInfoMap,
    occupancy: Optional[int] = None,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> Dict[FuelTypeEnum, float]:
    """Calculates the energy needs of machines in given household over given period

    Args:
        machine (MachineEnum): the machine
        machine_info (MachineInfoMap): info about the machine's energy use per day and its fuel type
        occupancy (int, optional): The number of people in the household. Defaults to None.
        period (PeriodEnum, optional): the period over which to calculate the energy use. Defaults to PeriodEnum.DAILY.

    Returns:
        Dict[FuelTypeEnum, float]: energy needs per fuel type of operating machine over given period in kWh
    """
    e_daily = get_energy_per_day(machine, machine_info, occupancy)
    e_daily_scaled = {
        fuel_type: scale_daily_to_period(e, period) for fuel_type, e in e_daily.items()
    }
    return e_daily_scaled


def get_total_appliance_energy(
    household: Household, period: PeriodEnum
) -> Dict[FuelTypeEnum, float]:

    space_heating_energy = get_energy_per_period(
        household.space_heating, SPACE_HEATING_INFO, household.occupancy, period
    )
    water_heating_energy = get_energy_per_period(
        household.water_heating, WATER_HEATING_INFO, household.occupancy, period
    )
    cooktop_energy = get_energy_per_period(
        household.cooktop, COOKTOP_INFO, household.occupancy, period
    )
    energy_dict = {}
    for fuel in FuelTypeEnum:
        # Exclude solar because the energy consumed from solar is calculated separately
        if fuel != FuelTypeEnum.SOLAR:
            energy_dict[fuel] = energy_dict.get(fuel, 0) + space_heating_energy.get(
                fuel, 0
            )
            energy_dict[fuel] += water_heating_energy.get(fuel, 0)
            energy_dict[fuel] += cooktop_energy.get(fuel, 0)

    return energy_dict


def get_vehicle_energy(
    vehicles: List[Vehicle], period: PeriodEnum = PeriodEnum.DAILY
) -> float:
    """Calculates the energy of a list of vehicles

    Args:
        vehicles (List[Vehicle]): the list of vehicles
        period (PeriodEnum, optional): the period over which to calculate the energy. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily energy value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: total NZD emitted from vehicles over given period to 2dp
    """
    total_energy = 0
    for vehicle in vehicles:
        if vehicle.fuel_type in [
            VehicleFuelTypeEnum.PLUG_IN_HYBRID,
            VehicleFuelTypeEnum.HYBRID,
        ]:
            avg_energy_daily = _get_hybrid_energy_per_day(vehicle.fuel_type)
        else:
            avg_energy_daily = get_energy_per_day(
                vehicle.fuel_type,
                VEHICLE_INFO,
            )

        # Weight the energy based on how much they use the vehicle compared to average
        weighting_factor = vehicle.kms_per_week / VEHICLE_AVG_KMS_PER_WEEK
        weighted_energy_daily = avg_energy_daily * weighting_factor

        # Convert to given period
        energy_period = scale_daily_to_period(weighted_energy_daily, period)

        # Add to total
        total_energy += energy_period
    return total_energy


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


def get_other_appliances_energy_per_period(
    occupancy: Optional[int] = None,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> Dict[FuelTypeEnum, float]:
    """Calculates the energy of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        occupancy (int, optional): The number of people in the household. Defaults to None.
        period (PeriodEnum, optional): the period over which to calculate the energy. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily energy value. Defaults to PeriodEnum.DAILY.

    Returns:
        Dict[FuelTypeEnum, float]: energy of operating other appliances over given period per fuel type
    """
    e_daily = {
        FuelTypeEnum.ELECTRICITY: scale_energy_by_occupancy(
            ENERGY_NEEDS_OTHER_MACHINES_PER_DAY, occupancy
        )
    }
    e_daily_scaled = {
        fuel_type: scale_daily_to_period(e, period) for fuel_type, e in e_daily.items()
    }
    return e_daily_scaled
