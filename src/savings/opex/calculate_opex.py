import pandas as pd
from typing import Optional, Tuple, List

from constants.machines.space_heating import (
    CENTRAL_SYSTEMS,
    INDIVIDUAL_SYSTEMS,
    SPACE_HEATING_KWH_PER_DAY,
    SPACE_HEATING_ELECTRIC_TYPES,
    SPACE_HEATING_REPLACEMENT_RATIOS,
    SPACE_HEATING_TYPE_TO_FUEL_TYPE,
)
from constants.machines.cooktop import (
    COOKTOP_ELECTRIC_TYPES,
    COOKTOP_KWH_PER_DAY,
    COOKTOP_COLS,
    COOKTOP_TYPE_TO_FUEL_TYPE,
)
from constants.machines.water_heating import (
    WATER_HEATING_ELECTRIC_TYPES,
    WATER_HEATING_OPEX_15_YRS,
    WATER_HEATING_KWH_PER_DAY,
    WATER_HEATING_TYPE_TO_FUEL_TYPE,
)
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from constants.machines.vehicles import (
    extract_vehicle_stats,
    VEHICLE_ELECTRIC_TYPES,
    VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA,
    RUCS,
)
from params import (
    SWITCH_TO,
    HOUSEHOLD_ENERGY_USE,
    OPERATIONAL_LIFETIME,
)
from constants.fuel_stats import COST_PER_FUEL_KWH_TODAY

from openapi_client.models import (
    Household,
    Opex,
    OpexValues,
)


def calculate_opex(
    current_household: Household, electrified_household: Household
) -> Opex:
    return Opex(
        perWeek=OpexValues(before=500.5, after=100.1, difference=400.4),
        perYear=OpexValues(before=500.5 * 52, after=100.1 * 52, difference=400.4 * 52),
        overLifetime=OpexValues(
            before=500.5 * 52 * 15 * 1.1,  # some random factor
            after=100.1 * 52 * 15 * 1.1,
            difference=400.4 * 52 * 15 * 1.1,
        ),
        operationalLifetime=15,
    )


# TODO: unit tests


def _get_machines_of_fuel_type(fuel_type: str, mapping: dict) -> List[str]:
    return [k for k, v in mapping.items() if v == fuel_type]


# Water heating needs to be treated separately
# TODO: make consistent data schema so we don't have these kinds of inconsistencies
NGAS_MACHINES = _get_machines_of_fuel_type(
    "natural_gas", COOKTOP_TYPE_TO_FUEL_TYPE
) + _get_machines_of_fuel_type("natural_gas", SPACE_HEATING_TYPE_TO_FUEL_TYPE)
LPG_MACHINES = _get_machines_of_fuel_type(
    "lpg", COOKTOP_TYPE_TO_FUEL_TYPE
) + _get_machines_of_fuel_type("lpg", SPACE_HEATING_TYPE_TO_FUEL_TYPE)

FIXED_COSTS_PER_YEAR = {
    "electricity": 689,  # on every home
    "natural_gas": 587,  # Machines!D292
    "lpg": 139,  # Machines!D293
}


# Solar savings

# TODO: Ideally we would calculate the exact house needs based on the appliances listed in survey responses
# plus extra appliances above, then calculate the actual consumption from grid, generation from solar, and amount sold to grid.
# But as a quick proxy, we're going to just take the average solar savings
# and apply it to all households in the dataset.

# Average total energy needs of home
# TODO: The below is wrong, just use the direct results from the sheet
# Use value from "Full home"!E25, when C8 Vehicle number is 0 and C12 Solar size is 5 kW
TOTAL_ELECTRICITY_NEEDS = 13.5  # kWh per day
POWER_BILL_NO_SOLAR = TOTAL_ELECTRICITY_NEEDS * COST_PER_FUEL_KWH_TODAY["electricity"]

# How much of the avg total energy needs can solar provide (free)?
SOLAR_SELF_CONSUMPTION_ON_APPLIANCES = 0.5  # C14
GENERATED_FROM_SOLAR = TOTAL_ELECTRICITY_NEEDS * SOLAR_SELF_CONSUMPTION_ON_APPLIANCES

# How much do you need from the grid, and how much does it cost?
CONSUMED_FROM_GRID = TOTAL_ELECTRICITY_NEEDS - GENERATED_FROM_SOLAR  # kWh/day
POWER_BILL_WITH_SOLAR = CONSUMED_FROM_GRID * COST_PER_FUEL_KWH_TODAY["electricity"]

# How much do you get from selling the rest to the grid?
FEED_IN_TARIFF = 0.12  # $ per kWh
REVENUE_FROM_SOLAR_EXPORT = GENERATED_FROM_SOLAR * 0.12  # $/day

# Average savings from solar per day
AVG_SAVINGS_FROM_SOLAR_ON_TOTAL_BILL_PER_DAY = (
    POWER_BILL_NO_SOLAR - POWER_BILL_WITH_SOLAR + REVENUE_FROM_SOLAR_EXPORT
)
AVG_SAVINGS_FROM_SOLAR_ON_TOTAL_BILL_PER_YEAR = (
    AVG_SAVINGS_FROM_SOLAR_ON_TOTAL_BILL_PER_DAY * 365.25
)
AVG_SAVINGS_FROM_SOLAR_ON_TOTAL_BILL_LIFETIME = (
    AVG_SAVINGS_FROM_SOLAR_ON_TOTAL_BILL_PER_YEAR * OPERATIONAL_LIFETIME
)


# average savings from solar on total bill per year straight from "Full Home" sheet
# without vehicles, 5 kWh solar panel, no battery, 12c feed-in
AVG_SAVINGS_FROM_SOLAR_0_VEHICLES_5KWH = 1035 * OPERATIONAL_LIFETIME
# with 2 vehicles, 7 kWh solar panel, no battery, 12c feed-in
AVG_SAVINGS_FROM_SOLAR_2_VEHICLES_7KWH = 1685 * OPERATIONAL_LIFETIME


# TODO: unit test
def enrich_opex(df: pd.DataFrame, with_solar=True) -> pd.DataFrame:
    """Enriches survey data with opex and opex savings data

    Args:
        df (pd.DataFrame): processed survey data

    Returns:
        pd.DataFrame: enriched dataframe with new ENRICHMENT_COLS_OPEX columns
    """
    # These are all values over the operational lifetime (15 years)
    df["vehicle_opex"], df["vehicle_opex_savings"] = zip(
        *df.apply(get_vehicle_opex_savings, axis=1)
    )
    df["space_heating_opex"], df["space_heating_opex_savings"] = zip(
        *df.apply(get_space_heating_opex_savings, axis=1)
    )
    df["water_heating_opex"], df["water_heating_opex_savings"] = zip(
        *df["Water heating"].apply(get_water_heating_opex_savings)
    )

    df["cooktop_opex"], df["cooktop_opex_savings"] = zip(
        *df[COOKTOP_COLS].apply(get_cooktop_opex_savings, axis=1)
    )
    df["fixed_costs_yearly"], df["fixed_costs_savings_yearly"] = zip(
        *df.apply(get_fixed_costs_per_year, axis=1)
    )
    df["fixed_costs_lifetime"] = df["fixed_costs_yearly"] * OPERATIONAL_LIFETIME
    df["fixed_costs_savings_lifetime"] = (
        df["fixed_costs_savings_yearly"] * OPERATIONAL_LIFETIME
    )

    # Totals

    ## Opex

    opex_extra_appliances_no_solar_lifetime = (
        ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
        * COST_PER_FUEL_KWH_TODAY["electricity"]
        * 365.25
        * OPERATIONAL_LIFETIME
    )

    ### without vehicles
    df["total_opex_lifetime_without_vehicles"] = (
        df["space_heating_opex"]
        + df["water_heating_opex"]
        + df["cooktop_opex"]
        + df["fixed_costs_lifetime"]
        + opex_extra_appliances_no_solar_lifetime
    )

    # Extra appliances

    ### with vehicles
    df["total_opex_lifetime_with_vehicles"] = (
        df["total_opex_lifetime_without_vehicles"] + df["vehicle_opex"]
    )

    ## Opex savings

    df["total_opex_savings_lifetime_base"] = (
        df["space_heating_opex_savings"]
        + df["water_heating_opex_savings"]
        + df["cooktop_opex_savings"]
        + df["fixed_costs_savings_lifetime"]
        # zero savings from extra appliances as they will still exist after electrification
    )

    ### without vehicles
    df["total_opex_savings_lifetime_without_vehicles"] = (
        (
            df["total_opex_savings_lifetime_base"]
            + AVG_SAVINGS_FROM_SOLAR_0_VEHICLES_5KWH
        )
        if with_solar
        else df["total_opex_savings_lifetime_base"]
    )
    df["opex_savings_without_vehicles_pct"] = (
        100
        * df["total_opex_savings_lifetime_without_vehicles"]
        / df["total_opex_lifetime_without_vehicles"]
    )

    ### with vehicles
    df["total_opex_savings_lifetime_with_vehicles"] = (
        df["total_opex_savings_lifetime_base"] + df["vehicle_opex_savings"]
    )
    if with_solar:
        df[
            "total_opex_savings_lifetime_with_vehicles"
        ] += AVG_SAVINGS_FROM_SOLAR_2_VEHICLES_7KWH
    df["opex_savings_with_vehicles_pct"] = (
        100
        * df["total_opex_savings_lifetime_with_vehicles"]
        / df["total_opex_lifetime_with_vehicles"]
    )

    return df


def get_fixed_costs_per_year(household: pd.Series) -> Tuple[float, float]:
    """Calculates the fixed costs you pay per year, for gas and LPG connections.
    Always includes electricity fixed costs, since all households pay this anyway
    for all the other devices we have (we assume the house stays on the grid).

    Args:
        household (pd.Series): info about one household

    Returns:
        float: $NZD cost per year
        float: $NZD savings per year from switching to electricity only
    """
    costs = FIXED_COSTS_PER_YEAR["electricity"]
    ngas_detected = False
    if (
        sum(household[NGAS_MACHINES].dropna()) > 0
        or household["Water heating"] == "Gas water heating"
    ):
        costs += FIXED_COSTS_PER_YEAR["natural_gas"]
        ngas_detected = True
    # If any mention of natural gas, use that over LPG even if they have both
    # (most homes won't actually have both, they'll just be referring to an LPG BBQ or something)
    if not ngas_detected:
        if (
            sum(household[LPG_MACHINES].dropna()) > 0
            or household["Water heating"] == "LPG water heating"
        ):
            costs += FIXED_COSTS_PER_YEAR["lpg"]

    # After electrification, fixed costs will just be electricity, so the savings is everything that's not electricity
    savings = costs - FIXED_COSTS_PER_YEAR["electricity"]
    return costs, savings
