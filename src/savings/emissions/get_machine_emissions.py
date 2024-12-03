from typing import List, Optional

from constants.machines.space_heating import SPACE_HEATING_ENERGY_LOCATION_MULTIPLIER
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.vehicle import Vehicle
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum

from constants.fuel_stats import EMISSIONS_FACTORS, FuelTypeEnum
from constants.machines.machine_info import MachineEnum, MachineInfoMap
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.vehicles import (
    VEHICLE_AVG_KMS_PER_WEEK,
    VEHICLE_INFO,
)
from constants.utils import PeriodEnum
from savings.energy.scale_energy_by_occupancy import scale_energy_by_occupancy
from utils.scale_daily_to_period import scale_daily_to_period


def get_emissions_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
    occupancy: Optional[int] = None,
    location: Optional[LocationEnum] = None,
) -> float:
    """Get emissions per day based on machine's energy use per day and emissions factor for fuel type

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type
        occupancy (int, optional): The number of people in the household.
        location (LocationEnum, optional): The location of the machine (for determining heating needs)

    Returns:
        float: machine's emissions in kgCO2e per day
    """
    # TODO: Use get_energy_per_day() for calculating energy, then just multiply by emissions factor
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    energy_scaled = scale_energy_by_occupancy(energy, occupancy)
    if type(machine_type) == SpaceHeatingEnum:
        multiplier = (
            1
            if location is None
            else SPACE_HEATING_ENERGY_LOCATION_MULTIPLIER[location]
        )
        energy_scaled = energy_scaled * multiplier
    emissions = energy_scaled * EMISSIONS_FACTORS[fuel_type]
    return emissions


def get_appliance_emissions(
    appliance: MachineEnum,
    appliance_info: MachineInfoMap,
    occupancy: Optional[int] = None,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the emissions from appliance in given household

    Args:
        appliance (MachineEnum): the appliance
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.
        occupancy (int, optional): The number of people in the household. Defaults to None.

    Returns:
        float: kgCO2e emitted from appliance over given period
    """
    emissions_daily = get_emissions_per_day(appliance, appliance_info, occupancy)
    return scale_daily_to_period(emissions_daily, period)


def get_other_appliance_emissions(
    occupancy: Optional[int] = None, period: PeriodEnum = PeriodEnum.DAILY
) -> float:
    """Calculates the emissions of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        occupancy (int, optional): The number of people in the household. Defaults to None.
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from other appliances over given period
    """
    energy_scaled = scale_energy_by_occupancy(
        ENERGY_NEEDS_OTHER_MACHINES_PER_DAY, occupancy
    )
    emissions_daily = energy_scaled * EMISSIONS_FACTORS[FuelTypeEnum.ELECTRICITY]
    return scale_daily_to_period(emissions_daily, period)


def get_vehicle_emissions(
    vehicles: List[Vehicle], period: PeriodEnum = PeriodEnum.DAILY
) -> float:
    """Calculates the emissions of a list of vehicles

    Args:
        vehicles (List[Vehicle]): the list of vehicles
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: total kgCO2e emitted from vehicles over given period
    """
    total_emissions = 0
    for vehicle in vehicles:
        if vehicle.fuel_type in [
            VehicleFuelTypeEnum.PLUG_IN_HYBRID,
            VehicleFuelTypeEnum.HYBRID,
        ]:
            avg_emissions_daily = _get_hybrid_emissions_per_day(vehicle.fuel_type)
        else:
            avg_emissions_daily = get_emissions_per_day(
                vehicle.fuel_type,
                VEHICLE_INFO,
            )

        # Weight the emissions based on how much they use the vehicle compared to average
        weighting_factor = vehicle.kms_per_week / VEHICLE_AVG_KMS_PER_WEEK
        weighted_emissions_daily = avg_emissions_daily * weighting_factor

        # Convert to given period
        emissions_period = scale_daily_to_period(weighted_emissions_daily, period)

        # Add to total
        total_emissions += emissions_period
    return total_emissions


def _get_hybrid_emissions_per_day(vehicle_type: VehicleFuelTypeEnum) -> float:
    petrol = get_emissions_per_day(
        VehicleFuelTypeEnum.PETROL,
        VEHICLE_INFO,
    )
    ev = get_emissions_per_day(
        VehicleFuelTypeEnum.ELECTRIC,
        VEHICLE_INFO,
    )
    if vehicle_type == VehicleFuelTypeEnum.PLUG_IN_HYBRID:
        # PHEV: Assume 60/40 split between petrol and electric
        return petrol * 0.6 + ev * 0.4
    if vehicle_type == VehicleFuelTypeEnum.HYBRID:
        # HEV: Assume 70/30 split between petrol and electric
        return petrol * 0.7 + ev * 0.3
