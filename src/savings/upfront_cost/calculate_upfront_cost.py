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
from savings.upfront_cost.get_machine_upfront_cost import (
    get_solar_upfront_cost,
    get_battery_upfront_cost,
    get_cooktop_upfront_cost,
    get_water_heating_upfront_cost,
    get_space_heating_upfront_cost,
)

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


# TODO: unit test


def calculate_upfront_cost(
    current_household: Household, electrified_household: Household
) -> UpfrontCost:
    return UpfrontCost(
        solar=get_solar_upfront_cost(current_household, electrified_household),
        battery=get_battery_upfront_cost(current_household, electrified_household),
        cooktop=get_cooktop_upfront_cost(current_household, electrified_household),
        waterHeating=get_water_heating_upfront_cost(
            current_household, electrified_household
        ),
        spaceHeating=get_space_heating_upfront_cost(
            current_household, electrified_household
        ),
    )


# ========= OLD =========


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
