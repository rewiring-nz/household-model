import pandas as pd
import math
from typing import Optional, Tuple

from constants.machines.space_heating import (
    CENTRAL_SYSTEMS,
    INDIVIDUAL_SYSTEMS,
    SPACE_HEATING_UPFRONT_COST,
    SPACE_HEATING_ELECTRIC_TYPES,
    SPACE_HEATING_REPLACEMENT_RATIOS,
)
from constants.machines.cooktop import (
    COOKTOP_ELECTRIC_TYPES,
    COOKTOP_UPFRONT_COST,
    COOKTOP_COLS,
)
from constants.machines.water_heating import (
    WATER_HEATING_ELECTRIC_TYPES,
    WATER_HEATING_UPFRONT_COST,
)
from params import SWITCH_TO, SOLAR_SIZE

SPACE_HEATING_SWITCH_TO_UPFRONT_COST = (
    SPACE_HEATING_UPFRONT_COST[SWITCH_TO["space_heating"]["switch_to_type"]][
        "item_price"
    ]
    + SPACE_HEATING_UPFRONT_COST[SWITCH_TO["space_heating"]["switch_to_type"]][
        "install_cost"
    ]
)

COOKTOP_SWITCH_TO_UPFRONT_COST = (
    COOKTOP_UPFRONT_COST[SWITCH_TO["cooktop"]["switch_to_type"]]["item_price"]
    + COOKTOP_UPFRONT_COST[SWITCH_TO["cooktop"]["switch_to_type"]]["install_cost"]
)

WATER_HEATING_SWITCH_TO_UPFRONT_COST = (
    WATER_HEATING_UPFRONT_COST[SWITCH_TO["water_heating"]["switch_to_type"]][
        "item_price"
    ]
    + WATER_HEATING_UPFRONT_COST[SWITCH_TO["water_heating"]["switch_to_type"]][
        "install_cost"
    ]
)

SOLAR_COST_PER_KW = 20500 / 9  # Doesn't take into account inverter
SOLAR_UPFRONT_COST = SOLAR_SIZE * SOLAR_COST_PER_KW

from openapi_client.models import (
    Household,
    UpfrontCost,
)


def calculate_upfront_cost(household: Household) -> UpfrontCost:
    return UpfrontCost(
        solar=15000.12,
        battery=7000.31,
        cooktop=500.50,
        waterHeating=3000.15,
        spaceHeating=3300.12,
    )


# TODO: unit tests
def enrich_upfront_cost(df: pd.DataFrame, with_solar=True) -> pd.DataFrame:
    """Enriches survey data with upfront cost info

    Args:
        df (pd.DataFrame): processed survey data

    Returns:
        pd.DataFrame: enriched dataframe with new ENRICHMENT_COLS_UPFRONT_COST columns
    """
    df["space_heating_upfront_cost"] = df.apply(get_space_heating_upfront_cost, axis=1)
    df["water_heating_upfront_cost"] = df["Water heating"].apply(
        get_water_heating_upfront_cost
    )
    df["cooktop_upfront_cost"] = df[COOKTOP_COLS].apply(
        get_cooktop_upfront_cost, axis=1
    )
    df["solar_upfront_cost"] = 0
    if with_solar:
        df["solar_upfront_cost"] = df["Solar"].apply(
            lambda x: 0 if x == "Yes" else SOLAR_COST_PER_KW * 7
        )
    df["total_upfront_cost"] = (
        df["space_heating_upfront_cost"]
        + df["water_heating_upfront_cost"]
        + df["cooktop_upfront_cost"]
        + df["solar_upfront_cost"]
    )
    return df


def get_space_heating_upfront_cost(household: pd.Series) -> Tuple[float, float]:
    """Calculates the upfront cost of switching fossil fuel home heaters to electric heat pump
    (split non-ducted).

    Args:
        household (pd.Series): info on the household including home heating info

    Returns:
        Optional[float]: upfront cost
    """
    n_total_replacements = 0

    # Central systems

    central_systems = household[CENTRAL_SYSTEMS]
    central_systems = central_systems[central_systems == 1].index.tolist()

    for heater_type in central_systems:
        # If it's a central heat pump or underfloor electric, don't replace
        if heater_type in (
            "Home heating_Heat pump central system (one indoor unit for the entire home)",
            "Home heating_Underfloor electric heating",
        ):
            continue

        # If it's a different electric type (e.g. resistive)
        if heater_type in SPACE_HEATING_ELECTRIC_TYPES:
            # but we are not switching existing electric machines, don't replace
            if not SWITCH_TO["space_heating"]["switch_if_electric"]:
                continue

        # Get the number of [heat pumps] we need to replace the power output of this system
        n_total_replacements += SPACE_HEATING_REPLACEMENT_RATIOS[heater_type]

    # Individual systems

    # Coalesce boolean columns with number columns for individual systems
    for bool_col, num_col in INDIVIDUAL_SYSTEMS.items():
        household[num_col] = (
            pd.Series([household.get(num_col), household.get(bool_col)]).dropna().max()
        )

    for num_col in set(INDIVIDUAL_SYSTEMS.values()):
        num_machines = household[num_col]
        if (
            pd.isna(num_machines)
            or num_machines == 0
            # If it's a heat pump, don't replace
            or num_col
            == "Home heating number_Heat pump split system (an individual unit in a room(s))"
            # If not switching existing electric machines
            or (
                num_col in SPACE_HEATING_ELECTRIC_TYPES
                and not SWITCH_TO["space_heating"]["switch_if_electric"]
            )
        ):
            continue

        n_total_replacements += SPACE_HEATING_REPLACEMENT_RATIOS[num_col] * num_machines

    # TODO "Other" free text field

    # Round up replacement ratio for capex
    total_upfront_cost = SPACE_HEATING_SWITCH_TO_UPFRONT_COST * math.ceil(
        n_total_replacements
    )

    return total_upfront_cost


def get_water_heating_upfront_cost(
    machine_type: str,
) -> Optional[float]:
    """Calculates the upfront cost to switch water heating to solar heat pump,
    if they are not already on one of the electric options.

    Args:
        machine_type (str): the type of water heating

    Returns:
        Optional[float]: upfront cost of switching to solar heat pump water heater
    """
    if machine_type == "Don’t know":
        return None

    if (
        machine_type in WATER_HEATING_ELECTRIC_TYPES
        and not SWITCH_TO["water_heating"]["switch_if_electric"]
    ):
        return 0

    return WATER_HEATING_SWITCH_TO_UPFRONT_COST


def get_cooktop_upfront_cost(
    cooktop_types: pd.Series,
) -> Optional[float]:
    """Calculates the upfront cost of switching fossil fuel cooktops
    to electric induction, if they don't already have an electric cooktop

    Args:
        cooktop_types (pd.Series): the number of each type of cooktop

    Returns:
        Optional[float]: upfront cost
    """

    cooktops = cooktop_types[cooktop_types == 1].index.tolist()

    # If they don't know, return None (not zero)
    if len(cooktops) == 1 and cooktops[0] == "Cooktop_Don't know":
        return None

    # Ignore savings for ones they don't know about
    cooktops_filtered = [x for x in cooktops if not (x == "Cooktop_Don't know")]

    # Don't switch if already electric
    if not SWITCH_TO["cooktop"]["switch_if_electric"]:
        cooktops_filtered = [x for x in cooktops if x not in COOKTOP_ELECTRIC_TYPES]

    if len(cooktops_filtered) == 0:
        return 0

    return COOKTOP_SWITCH_TO_UPFRONT_COST * len(cooktops_filtered)
