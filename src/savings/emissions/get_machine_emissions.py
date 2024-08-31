from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.machine_info import MachineEnum, MachineInfoMap
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from openapi_client.models.vehicle import Vehicle
from params import OPERATIONAL_LIFETIME
from constants.utils import PeriodEnum

import pandas as pd
from typing import List, Optional, Tuple

from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.space_heating import (
    SPACE_HEATING_INFO,
)
from constants.machines.vehicles import (
    VEHICLE_ELECTRIC_TYPES,
    VEHICLE_INFO,
    VEHICLE_TYPE_TO_FUEL_TYPE,
    VEHICLE_FUEL_TYPE_COLS,
    VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA,
    VEHICLE_EMBODIED_EMISSIONS,
    extract_vehicle_stats,
)
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.utils import PeriodEnum
from params import OPERATIONAL_LIFETIME


def get_emissions_per_day(
    machine_type: MachineEnum,
    machine_stats_map: MachineInfoMap,
) -> float:
    """Get emissions per day based on machine's energy use per day and emissions factor for fuel type

    Args:
        machine_type (MachineEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (MachineInfoMap): info about the machine's energy use per day and its fuel type

    Returns:
        float: machine's emissions in kgCO2e per day
    """
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    emissions = energy * EMISSIONS_FACTORS[fuel_type]
    return emissions


def get_appliance_emissions(
    appliance: MachineEnum,
    appliance_info: MachineInfoMap,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the emissions from appliance in given household

    Args:
        appliance (MachineEnum): the appliance
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from appliance over given period
    """
    emissions_daily = get_emissions_per_day(
        appliance,
        appliance_info,
    )
    return _convert_to_period(emissions_daily, period)


def get_other_appliance_emissions(period: PeriodEnum = PeriodEnum.DAILY) -> float:
    """Calculates the emissions of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from other appliances over given period
    """
    emissions_daily = (
        ENERGY_NEEDS_OTHER_MACHINES_PER_DAY * EMISSIONS_FACTORS["electricity"]
    )
    return _convert_to_period(emissions_daily, period)


def get_vehicle_emissions(
    vehicles: List[Vehicle], period: PeriodEnum = PeriodEnum.DAILY
) -> float:
    total_emissions = 0
    for vehicle in vehicles:
        # PHEV: Assume 60/40 split between petrol and electric
        # HEV: Assume 70/30 split between petrol and electric
        avg_emissions_daily = get_emissions_per_day(
            vehicle.fuel_type,
            VEHICLE_INFO,
        )

        # Weight the emissions based on how much they use the vehicle compared to average
        weighting_factor = (
            vehicle.kms_per_week * 52 / VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA
        )
        weighted_emissions_daily = avg_emissions_daily * weighting_factor

        # Convert to given period
        emissions_period = _convert_to_period(weighted_emissions_daily, period)

        # Add to total
        total_emissions += emissions_period
    return total_emissions


def _convert_to_period(emissions_daily: float, period: PeriodEnum) -> float:
    # This might become more complex in future, taking into account macroeconomic effects
    if period == PeriodEnum.DAILY:
        return emissions_daily
    if period == PeriodEnum.WEEKLY:
        return emissions_daily * 7
    if period == PeriodEnum.YEARLY:
        return emissions_daily * 365.25
    if period == PeriodEnum.OPERATIONAL_LIFETIME:
        return emissions_daily * 365.25 * OPERATIONAL_LIFETIME
