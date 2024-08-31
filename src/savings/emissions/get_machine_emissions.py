from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.appliance import ApplianceEnum, ApplianceInfo
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from params import OPERATIONAL_LIFETIME
from constants.utils import PeriodEnum

import pandas as pd
from typing import Optional, Tuple

from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.space_heating import (
    SPACE_HEATING_INFO,
)
from constants.machines.vehicles import (
    VEHICLE_KWH_PER_DAY,
    VEHICLE_ELECTRIC_TYPES,
    VEHICLE_TYPE_TO_FUEL_TYPE,
    VEHICLE_FUEL_TYPE_COLS,
    VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA,
    VEHICLE_EMBODIED_EMISSIONS,
    extract_vehicle_stats,
)
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.utils import PeriodEnum
from params import (
    SWITCH_TO,
    VEHICLE_SWITCH_TO_EMISSIONS_RUNNING,
    VEHICLE_SWITCH_TO_EMISSIONS_EMBODIED,
    OPERATIONAL_LIFETIME,
)


def get_emissions_per_day(
    machine_type: ApplianceEnum,
    machine_stats_map: ApplianceInfo,
) -> float:
    """Get emissions per day based on machine's energy use per day and emissions factor for fuel type

    Args:
        machine_type (ApplianceEnum): the type of machine, e.g. a gas cooktop
        machine_stats_map (ApplianceInfo): info about the machine's energy use per day and its fuel type

    Returns:
        float: machine's emissions in kgCO2e per day
    """
    energy = machine_stats_map[machine_type]["kwh_per_day"]
    fuel_type = machine_stats_map[machine_type]["fuel_type"]
    emissions = energy * EMISSIONS_FACTORS[fuel_type]
    return emissions


def get_appliance_emissions(
    appliance: ApplianceEnum,
    appliance_info: ApplianceInfo,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the emissions from appliance in given household

    Args:
        appliance (ApplianceEnum): the appliance
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
    household: pd.Series,
) -> Tuple[Optional[float], Optional[float]]:
    vehicle_stats = extract_vehicle_stats(household)

    if len(vehicle_stats) == 0:
        return 0, 0

    total_emissions = 0
    total_savings = 0
    for v in vehicle_stats:

        if v["fuel_type"] not in ["Plug-in Hybrid", "Hybrid"]:
            avg_running_emissions = get_emissions_per_day_old(
                v["fuel_type"],
                VEHICLE_KWH_PER_DAY,
                VEHICLE_TYPE_TO_FUEL_TYPE,
            )
        if v["fuel_type"] == "Plug-in Hybrid":
            # Assume 60/40 split between petrol and electric
            petrol_portion_emissions = (
                get_emissions_per_day_old(
                    "Petrol",
                    VEHICLE_KWH_PER_DAY,
                    VEHICLE_TYPE_TO_FUEL_TYPE,
                )
                * 0.6
            )
            electric_portion_emissions = (
                get_emissions_per_day_old(
                    "Electric",
                    VEHICLE_KWH_PER_DAY,
                    VEHICLE_TYPE_TO_FUEL_TYPE,
                )
                * 0.4
            )
            avg_running_emissions = (
                petrol_portion_emissions + electric_portion_emissions
            )
        if v["fuel_type"] == "Hybrid":
            # Assume 70/30 split between petrol and electric
            petrol_portion_emissions = (
                get_emissions_per_day_old(
                    "Petrol",
                    VEHICLE_KWH_PER_DAY,
                    VEHICLE_TYPE_TO_FUEL_TYPE,
                )
                * 0.7
            )
            electric_portion_emissions = (
                get_emissions_per_day_old(
                    "Electric",
                    VEHICLE_KWH_PER_DAY,
                    VEHICLE_TYPE_TO_FUEL_TYPE,
                )
                * 0.3
            )
            avg_running_emissions = (
                petrol_portion_emissions + electric_portion_emissions
            )

        # Get % of average vehicle use based on distance
        pct_of_avg = v["distance_per_yr"] / VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA
        running_emissions = avg_running_emissions * pct_of_avg

        # # The emissions from producing the car + battery, per day
        # # TODO: make it optional to include/exclude embodied emissions
        # if v['fuel_type'] not in ['Plug-in Hybrid', 'Hybrid']:
        #     embodied_emissions = (
        #         VEHICLE_EMBODIED_EMISSIONS[v['fuel_type']]
        #         / OPERATIONAL_LIFETIME
        #         / 365.25
        #     )
        # if v['fuel_type'] == 'Plug-in Hybrid':
        #     # Again, a 60/40 split
        #     petrol_portion_embodied = (
        #         VEHICLE_EMBODIED_EMISSIONS['Petrol'] / OPERATIONAL_LIFETIME / 365.25
        #     ) * 0.6
        #     electric_portion_embodied = (
        #         VEHICLE_EMBODIED_EMISSIONS['Electric'] / OPERATIONAL_LIFETIME / 365.25
        #     ) * 0.4
        #     embodied_emissions = petrol_portion_embodied + electric_portion_embodied
        # if v['fuel_type'] == 'Hybrid':
        #     # Again, 70/30 split (even though it's probably more like 90/10)
        #     petrol_portion_embodied = (
        #         VEHICLE_EMBODIED_EMISSIONS['Petrol'] / OPERATIONAL_LIFETIME / 365.25
        #     ) * 0.7
        #     electric_portion_embodied = (
        #         VEHICLE_EMBODIED_EMISSIONS['Electric'] / OPERATIONAL_LIFETIME / 365.25
        #     ) * 0.3
        #     embodied_emissions = petrol_portion_embodied + electric_portion_embodied

        # total_vehicle_emissions = running_emissions + embodied_emissions
        total_vehicle_emissions = running_emissions

        total_emissions += total_vehicle_emissions
        ev_emissions = (
            VEHICLE_SWITCH_TO_EMISSIONS_RUNNING
            * pct_of_avg
            # + VEHICLE_SWITCH_TO_EMISSIONS_EMBODIED
        )
        savings = total_vehicle_emissions - ev_emissions
        if (
            v["fuel_type"] in VEHICLE_ELECTRIC_TYPES
            and not SWITCH_TO["vehicle"]["switch_if_electric"]
        ):
            # Don't switch if they're already on electric
            savings = 0
        total_savings += savings
    return total_emissions, total_savings


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
