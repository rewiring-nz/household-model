import pandas as pd
from typing import Tuple, List

from constants.machines.space_heating import (
    SPACE_HEATING_INFO,
    SPACE_HEATING_TYPE_TO_FUEL_TYPE,
)
from constants.machines.cooktop import (
    COOKTOP_INFO,
    COOKTOP_TYPE_TO_FUEL_TYPE,
)
from constants.machines.water_heating import (
    WATER_HEATING_INFO,
)
from constants.utils import PeriodEnum
from params import (
    OPERATIONAL_LIFETIME,
)
from constants.fuel_stats import COST_PER_FUEL_KWH_TODAY

from openapi_client.models import (
    Household,
    Opex,
    OpexValues,
)
from savings.opex.get_solar_savings import get_solar_savings
from savings.opex.get_machine_opex import (
    get_appliance_opex,
    get_fixed_costs,
    get_other_appliance_opex,
    get_vehicle_opex,
)


def calculate_opex(
    current_household: Household, electrified_household: Household
) -> Opex:

    # Weekly
    weekly_before = _get_total_opex(current_household, PeriodEnum.WEEKLY)
    weekly_after = _get_total_opex(electrified_household, PeriodEnum.WEEKLY)

    # Yearly
    yearly_before = _get_total_opex(current_household, PeriodEnum.YEARLY)
    yearly_after = _get_total_opex(electrified_household, PeriodEnum.YEARLY)

    # Operational lifetime
    lifetime_before = _get_total_opex(
        current_household, PeriodEnum.OPERATIONAL_LIFETIME
    )
    lifetime_after = _get_total_opex(
        electrified_household, PeriodEnum.OPERATIONAL_LIFETIME
    )

    return Opex(
        perWeek=OpexValues(
            before=round(weekly_before, 2),
            after=round(weekly_after, 2),
            difference=round(weekly_after - weekly_before, 2),
        ),
        perYear=OpexValues(
            before=round(yearly_before, 2),
            after=round(yearly_after, 2),
            difference=round(yearly_after - yearly_before, 2),
        ),
        overLifetime=OpexValues(
            before=round(lifetime_before, 2),
            after=round(lifetime_after, 2),
            difference=round(lifetime_after - lifetime_before, 2),
        ),
        operationalLifetime=OPERATIONAL_LIFETIME,
    )


def _get_total_opex(household: Household, period: PeriodEnum):
    appliance_opex = _get_total_appliance_opex(household, period)
    vehicle_opex = get_vehicle_opex(household.vehicles, period)
    other_opex = get_other_appliance_opex(period)
    fixed_costs = get_fixed_costs(household, period)
    solar_savings = get_solar_savings(household.solar)
    return appliance_opex + vehicle_opex + other_opex + fixed_costs - solar_savings


def _get_total_appliance_opex(household: Household, period: PeriodEnum):
    return (
        get_appliance_opex(household.space_heating, SPACE_HEATING_INFO, period)
        + get_appliance_opex(household.water_heating, WATER_HEATING_INFO, period)
        + get_appliance_opex(household.cooktop, COOKTOP_INFO, period)
    )


# ============ OLD ============


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
