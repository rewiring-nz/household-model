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

from openapi_client.models import (
    Household,
    Emissions,
    EmissionsValues,
)
from savings.emissions.get_appliance_emissions import (
    get_appliance_emissions,
    get_other_appliance_emissions,
)
from savings.emissions.get_emissions_per_day import get_emissions_per_day_old


def calculate_emissions(
    current_household: Household, electrified_household: Household
) -> Emissions:

    # Weekly
    space_heating_emissions_weekly_before = get_appliance_emissions(
        current_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    space_heating_emissions_weekly_after = get_appliance_emissions(
        electrified_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    water_heating_emissions_weekly_before = get_appliance_emissions(
        current_household.water_heating, WATER_HEATING_INFO, PeriodEnum.WEEKLY
    )
    water_heating_emissions_weekly_after = get_appliance_emissions(
        electrified_household.water_heating, WATER_HEATING_INFO, PeriodEnum.WEEKLY
    )
    cooktop_emissions_weekly_before = get_appliance_emissions(
        current_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY
    )
    cooktop_emissions_weekly_after = get_appliance_emissions(
        electrified_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY
    )
    # TODO: vehicle emissions
    other_emissions_weekly_before = get_other_appliance_emissions(PeriodEnum.WEEKLY)
    other_emissions_weekly_after = get_other_appliance_emissions(PeriodEnum.WEEKLY)

    # We use the function to get emissions over longer periods, rather than relying on straight multiplication for emissions over operational lifetime, since macroeconomic factors can change things.

    # Yearly
    space_heating_emissions_yearly_before = get_appliance_emissions(
        current_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.YEARLY
    )
    space_heating_emissions_yearly_after = get_appliance_emissions(
        electrified_household.space_heating, SPACE_HEATING_INFO, PeriodEnum.YEARLY
    )
    water_heating_emissions_yearly_before = get_appliance_emissions(
        current_household.water_heating, WATER_HEATING_INFO, PeriodEnum.YEARLY
    )
    water_heating_emissions_yearly_after = get_appliance_emissions(
        electrified_household.water_heating, WATER_HEATING_INFO, PeriodEnum.YEARLY
    )
    cooktop_emissions_yearly_before = get_appliance_emissions(
        current_household.cooktop, COOKTOP_INFO, PeriodEnum.YEARLY
    )
    cooktop_emissions_yearly_after = get_appliance_emissions(
        electrified_household.cooktop, COOKTOP_INFO, PeriodEnum.YEARLY
    )
    other_emissions_yearly_before = get_other_appliance_emissions(PeriodEnum.YEARLY)
    other_emissions_yearly_after = get_other_appliance_emissions(PeriodEnum.YEARLY)

    # Operational lifetime
    space_heating_emissions_lifetime_before = get_appliance_emissions(
        current_household.space_heating,
        SPACE_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    space_heating_emissions_lifetime_after = get_appliance_emissions(
        electrified_household.space_heating,
        SPACE_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    water_heating_emissions_lifetime_before = get_appliance_emissions(
        current_household.water_heating,
        WATER_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    water_heating_emissions_lifetime_after = get_appliance_emissions(
        electrified_household.water_heating,
        WATER_HEATING_INFO,
        PeriodEnum.OPERATIONAL_LIFETIME,
    )
    cooktop_emissions_lifetime_before = get_appliance_emissions(
        current_household.cooktop, COOKTOP_INFO, PeriodEnum.OPERATIONAL_LIFETIME
    )
    cooktop_emissions_lifetime_after = get_appliance_emissions(
        electrified_household.cooktop, COOKTOP_INFO, PeriodEnum.OPERATIONAL_LIFETIME
    )
    other_emissions_lifetime_before = get_other_appliance_emissions(
        PeriodEnum.OPERATIONAL_LIFETIME
    )
    other_emissions_lifetime_after = get_other_appliance_emissions(
        PeriodEnum.OPERATIONAL_LIFETIME
    )

    # Total emissions before
    weekly_before = (
        space_heating_emissions_weekly_before
        + water_heating_emissions_weekly_before
        + cooktop_emissions_weekly_before
        + other_emissions_weekly_before
    )
    yearly_before = (
        space_heating_emissions_yearly_before
        + water_heating_emissions_yearly_before
        + cooktop_emissions_yearly_before
        + other_emissions_yearly_before
    )
    lifetime_before = (
        space_heating_emissions_lifetime_before
        + water_heating_emissions_lifetime_before
        + cooktop_emissions_lifetime_before
        + other_emissions_lifetime_before
    )

    # Total emissions after
    weekly_after = (
        space_heating_emissions_weekly_after
        + water_heating_emissions_weekly_after
        + cooktop_emissions_weekly_after
        + other_emissions_weekly_after
    )
    yearly_after = (
        space_heating_emissions_yearly_after
        + water_heating_emissions_yearly_after
        + cooktop_emissions_yearly_after
        + other_emissions_yearly_after
    )
    lifetime_after = (
        space_heating_emissions_lifetime_after
        + water_heating_emissions_lifetime_after
        + cooktop_emissions_lifetime_after
        + other_emissions_lifetime_after
    )

    return Emissions(
        perWeek=EmissionsValues(
            before=weekly_before,
            after=weekly_after,
            difference=weekly_after - weekly_before,
        ),
        perYear=EmissionsValues(
            before=yearly_before,
            after=yearly_after,
            difference=yearly_after - yearly_before,
        ),
        overLifetime=EmissionsValues(
            before=lifetime_before,
            after=lifetime_after,
            difference=lifetime_after - lifetime_before,
        ),
        operationalLifetime=OPERATIONAL_LIFETIME,
    )


def get_vehicle_emissions_savings(
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
