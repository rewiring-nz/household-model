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


def get_space_heating_emissions(
    household: pd.Series, household_energy_use: Optional[float] = HOUSEHOLD_ENERGY_USE
) -> Tuple[float, float]:
    pass


def get_space_heating_emissions_savings(
    household: pd.Series, household_energy_use: Optional[float] = HOUSEHOLD_ENERGY_USE
) -> Tuple[float, float]:
    """Calculates the emissions from fossil fuel home heaters, and potential
    savings from switching fossil fuel home heaters to electric heat pump
    (split non-ducted).

    Args:
        household (pd.Series): info on the household including home heating info

    Returns:
        float: kgCO2e/day emitted from fossil fuel heating sources
        float: kgCO2e/day saved if they electrified all their heating
    """
    total_emissions_before = 0
    total_emissions_after = 0
    n_total_replacements = 0

    # Central systems

    central_systems = household[CENTRAL_SYSTEMS]
    central_systems = central_systems[central_systems == 1].index.tolist()

    for heater_type in central_systems:
        emissions = get_emissions_per_day(
            heater_type,
            SPACE_HEATING_KWH_PER_DAY,
            SPACE_HEATING_TYPE_TO_FUEL_TYPE,
            household_energy_use,
        )
        total_emissions_before += emissions

        # If it's a central heat pump or underfloor electric, don't replace
        if heater_type in (
            "Home heating_Heat pump central system (one indoor unit for the entire home)",
            "Home heating_Underfloor electric heating",
        ):
            total_emissions_after += emissions
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
        if pd.isna(num_machines) or num_machines == 0:
            continue

        emissions = get_emissions_per_day(
            num_col,
            SPACE_HEATING_KWH_PER_DAY,
            SPACE_HEATING_TYPE_TO_FUEL_TYPE,
            household_energy_use,
        )
        total_emissions_before += emissions * num_machines

        # If it's a heat pump, don't replace
        if num_col in (
            "Home heating number_Heat pump split system (an individual unit in a room(s))",
        ):
            total_emissions_after += emissions * num_machines
            continue

        # # If it's a different electric type (e.g. resistive) but we are not switching existing electric machines, don't replace
        if (
            num_col in SPACE_HEATING_ELECTRIC_TYPES
            and not SWITCH_TO["space_heating"]["switch_if_electric"]
        ):
            continue

        n_total_replacements += SPACE_HEATING_REPLACEMENT_RATIOS[num_col] * num_machines

    # TODO "Other" free text field
    total_emissions_after += SPACE_HEATING_SWITCH_TO_EMISSIONS * n_total_replacements
    total_savings = total_emissions_before - total_emissions_after
    return total_emissions_before, total_savings
