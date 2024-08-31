import pandas as pd
from typing import Optional, Tuple

from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.space_heating import (
    SPACE_HEATING_ELECTRIC_TYPES,
    SPACE_HEATING_KWH_PER_DAY,
    SPACE_HEATING_TYPE_TO_FUEL_TYPE,
    CENTRAL_SYSTEMS,
    INDIVIDUAL_SYSTEMS,
    SPACE_HEATING_REPLACEMENT_RATIOS,
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
from params import (
    SWITCH_TO,
    HOUSEHOLD_ENERGY_USE,
    SPACE_HEATING_SWITCH_TO_EMISSIONS,
    WATER_HEATING_SWITCH_TO_EMISSIONS,
    COOKTOP_SWITCH_TO_EMISSIONS,
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
from savings.emissions.get_space_heating_emissions import (
    get_space_heating_emissions,
    get_space_heating_emissions_savings,  # TODO: remove once we're working just with the emissions func
)
from savings.emissions.get_emissions_per_day import get_emissions_per_day_old

# Other machines (space cooling, refrigeration, laundry, lighting, etc. assume all electric)
EMISSIONS_OTHER_MACHINES = (
    ENERGY_NEEDS_OTHER_MACHINES_PER_DAY * EMISSIONS_FACTORS["electricity"]
)  # kgCO2e/day


def calculate_emissions(household: Household) -> Emissions:
    return Emissions(
        perWeek=EmissionsValues(before=500.5, after=100.1, difference=400.4),
        perYear=EmissionsValues(
            before=500.5 * 52, after=100.1 * 52, difference=400.4 * 52
        ),
        overLifetime=EmissionsValues(
            before=500.5 * 52 * 15 * 1.1,  # some random factor
            after=100.1 * 52 * 15 * 1.1,
            difference=400.4 * 52 * 15 * 1.1,
        ),
        operationalLifetime=15,
    )


# TODO: unit test
def enrich_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """Enriches survey data with emissions and emissions savings data

    Args:
        df (pd.DataFrame): processed survey data

    Returns:
        pd.DataFrame: enriched dataframe with new ENRICHMENT_COLS_EMISSIONS columns
    """

    # Machines
    df["space_heating_emissions"], df["space_heating_emissions_savings"] = zip(
        *df.apply(get_space_heating_emissions_savings, axis=1)
    )
    df["water_heating_emissions"], df["water_heating_emissions_savings"] = zip(
        *df["Water heating"].apply(get_water_heating_emissions_savings)
    )
    cooktop_cols = [x for x in df.columns if "Cooktop_" in x]
    df["cooktop_emissions"], df["cooktop_emissions_savings"] = zip(
        *df[cooktop_cols].apply(get_cooktop_emissions_savings, axis=1)
    )
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


# TODO: unit test
def get_water_heating_emissions_savings(
    machine_type: str, household_energy_use: Optional[float] = HOUSEHOLD_ENERGY_USE
) -> Tuple[Optional[float], Optional[float]]:
    """Calculates the emissions savings from switching water heating

    Args:
        machine_type (str): the type of water heating

    Returns:
        Optional[float]: kgCO2e/day emitted from fossil fuel heating sources
        Optional[float]: kgCO2e/day saved if they switched to electric
    """
    # Basically the formula in 'Full home'!D79

    if machine_type == "Don’t know":
        return None, None

    energy = WATER_HEATING_KWH_PER_DAY[machine_type] * household_energy_use  # kWh/day
    fuel_type = WATER_HEATING_TYPE_TO_FUEL_TYPE[machine_type]
    emissions = energy * EMISSIONS_FACTORS[fuel_type]  # kgCO2e/kWh

    savings = emissions - WATER_HEATING_SWITCH_TO_EMISSIONS
    if (
        machine_type in WATER_HEATING_ELECTRIC_TYPES
        and not SWITCH_TO["water_heating"]["switch_if_electric"]
    ):
        savings = 0
    return emissions, savings


def get_cooktop_emissions_savings(
    cooktop_types: pd.Series,
    household_energy_use: Optional[float] = HOUSEHOLD_ENERGY_USE,
) -> Tuple[Optional[float], Optional[float]]:
    """Calculates the emissions savings from switching fossil fuel cooktop
    to electric induction, if they don't already have an electric cooktop

    Args:
        cooktop_types (pd.Series): the number of each type of cooktop

    Returns:
        Optional[float]: kgCO2e/day emitted by fossil fuel machines
        Optional[float]: kgCO2e/day saved if they switched all their cooktops to electric
    """

    cooktops = cooktop_types[cooktop_types == 1].index.tolist()

    # If they don't know, return None (not zero)
    if len(cooktops) == 1 and cooktops[0] == "Cooktop_Don't know":
        return None, None

    # Ignore savings for ones they don't know about
    cooktops_filtered = [x for x in cooktops if x != "Cooktop_Don't know"]

    # For everyone else, calculating savings for switching to electric induction
    total_emissions = 0
    total_savings = 0
    for ct in cooktops_filtered:
        emissions = get_emissions_per_day_old(
            ct,
            COOKTOP_KWH_PER_DAY,
            COOKTOP_TYPE_TO_FUEL_TYPE,
            household_energy_use,
        )
        total_emissions += emissions
        savings = emissions - COOKTOP_SWITCH_TO_EMISSIONS
        if (
            ct in COOKTOP_ELECTRIC_TYPES
            and not SWITCH_TO["cooktop"]["switch_if_electric"]
        ):
            # Don't switch if they're already on electric
            savings = 0
        total_savings += savings
    return total_emissions, total_savings


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
