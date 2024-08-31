import pandas as pd
from typing import Optional, Tuple

from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.space_heating import (
    SPACE_HEATING_INFO,
)
from constants.machines.cooktop import (
    COOKTOP_KWH_PER_DAY,
    COOKTOP_TYPE_TO_FUEL_TYPE,
    COOKTOP_ELECTRIC_TYPES,
)
from constants.machines.water_heating import (
    WATER_HEATING_KWH_PER_DAY,
    WATER_HEATING_ELECTRIC_TYPES,
    WATER_HEATING_TYPE_TO_FUEL_TYPE,
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
    SpaceHeatingEnum,
)
from savings.emissions.get_appliance_emissions import (
    get_appliance_emissions,
)
from savings.emissions.get_emissions_per_day import get_emissions_per_day_old

# Other machines (space cooling, refrigeration, laundry, lighting, etc. assume all electric)
EMISSIONS_OTHER_MACHINES = (
    ENERGY_NEEDS_OTHER_MACHINES_PER_DAY * EMISSIONS_FACTORS["electricity"]
)  # kgCO2e/day


def calculate_emissions(
    current_household: Household, electrified_household: Household
) -> Emissions:

    # Weekly
    space_heating_emissions_weekly_before = get_appliance_emissions(
        current_household, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    space_heating_emissions_weekly_after = get_appliance_emissions(
        electrified_household, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    water_heating_emissions_weekly_before = get_appliance_emissions(
        current_household, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )
    water_heating_emissions_weekly_after = get_appliance_emissions(
        electrified_household, SPACE_HEATING_INFO, PeriodEnum.WEEKLY
    )

    # We use the function to get emissions over longer periods, rather than relying on straight multiplication for emissions over operational lifetime, since macroeconomic factors can change things.

    # Yearly
    space_heating_emissions_yearly_before = get_appliance_emissions(
        current_household, SPACE_HEATING_INFO, PeriodEnum.YEARLY
    )
    space_heating_emissions_yearly_after = get_appliance_emissions(
        electrified_household, SPACE_HEATING_INFO, PeriodEnum.YEARLY
    )

    # Operational lifetime
    space_heating_emissions_lifetime_before = get_appliance_emissions(
        current_household, SPACE_HEATING_INFO, PeriodEnum.OPERATIONAL_LIFETIME
    )
    space_heating_emissions_lifetime_after = get_appliance_emissions(
        electrified_household, SPACE_HEATING_INFO, PeriodEnum.OPERATIONAL_LIFETIME
    )

    # Total emissions before
    weekly_before = space_heating_emissions_weekly_before  # + water_heating_emissions_weekly_before etc.
    yearly_before = space_heating_emissions_yearly_before  # + water_heating_emissions_yearly_before etc.
    lifetime_before = space_heating_emissions_lifetime_before  # + water_heating_emissions_lifetime_before etc.

    # Total emissions after
    weekly_after = space_heating_emissions_weekly_after  # + water_heating_emissions_weekly_after etc.
    yearly_after = space_heating_emissions_yearly_after  # + water_heating_emissions_yearly_after etc.
    lifetime_after = space_heating_emissions_lifetime_after  # + water_heating_emissions_lifetime_after etc.

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


# TODO: unit test
def enrich_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """Enriches survey data with emissions and emissions savings data

    Args:
        df (pd.DataFrame): processed survey data

    Returns:
        pd.DataFrame: enriched dataframe with new ENRICHMENT_COLS_EMISSIONS columns
    """
    df["vehicle_emissions"], df["vehicle_emissions_savings"] = zip(
        *df.apply(get_vehicle_emissions_savings, axis=1)
    )

    # Totals

    ## Emissions

    ### without vehicles
    df["total_emissions_without_vehicles"] = (
        df["space_heating_emissions"]
        + df["water_heating_emissions"]
        + df["cooktop_emissions"]
        + EMISSIONS_OTHER_MACHINES
    )
    df["total_emissions_without_vehicles_year"] = (
        df["total_emissions_without_vehicles"] * 365.25
    )
    df["total_emissions_without_vehicles_lifetime"] = (
        df["total_emissions_without_vehicles_year"] * OPERATIONAL_LIFETIME
    )

    ### with vehicles
    df["total_emissions_with_vehicles"] = (
        df["total_emissions_without_vehicles"] + df["vehicle_emissions"]
    )
    df["total_emissions_with_vehicles_year"] = (
        df["total_emissions_with_vehicles"] * 365.25
    )
    df["total_emissions_with_vehicles_lifetime"] = (
        df["total_emissions_with_vehicles_year"] * OPERATIONAL_LIFETIME
    )

    ## Emissions savings

    ### without vehicles
    df["total_emissions_savings_without_vehicles"] = (
        df["space_heating_emissions_savings"]
        + df["water_heating_emissions_savings"]
        + df["cooktop_emissions_savings"]
        # Other machines are already assumed electric, so won't be switched and therefore won't bring any savings
    )
    df["total_emissions_savings_without_vehicles_year"] = (
        df["total_emissions_savings_without_vehicles"] * 365.25
    )
    df["total_emissions_savings_without_vehicles_lifetime"] = (
        df["total_emissions_savings_without_vehicles_year"] * OPERATIONAL_LIFETIME
    )

    df["emissions_savings_without_vehicles_pct"] = (
        100
        * df["total_emissions_savings_without_vehicles"]
        / df["total_emissions_without_vehicles"]
    )

    ### with vehicles
    df["total_emissions_savings_with_vehicles"] = (
        df["total_emissions_savings_without_vehicles"] + df["vehicle_emissions_savings"]
    )
    df["total_emissions_savings_with_vehicles_year"] = (
        df["total_emissions_savings_with_vehicles"] * 365.25
    )
    df["total_emissions_savings_with_vehicles_lifetime"] = (
        df["total_emissions_savings_with_vehicles_year"] * OPERATIONAL_LIFETIME
    )

    df["emissions_savings_with_vehicles_pct"] = (
        100
        * df["total_emissions_savings_with_vehicles"]
        / df["total_emissions_with_vehicles"]
    )

    return df


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
