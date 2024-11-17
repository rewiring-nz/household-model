from constants.machines.space_heating import (
    SPACE_HEATING_INFO,
)
from constants.machines.cooktop import (
    COOKTOP_INFO,
)
from constants.machines.water_heating import (
    WATER_HEATING_INFO,
)
from constants.utils import PeriodEnum
from params import (
    OPERATIONAL_LIFETIME,
)
from constants.fuel_stats import COST_PER_FUEL_KWH_TODAY, FuelTypeEnum

from openapi_client.models import (
    Household,
    Opex,
    OpexValues,
)
from savings.energy.get_machine_energy import (
    get_energy_per_period,
    get_total_energy_needs,
)
from savings.opex.get_machine_opex import (
    get_other_appliances_opex_per_period,
    get_vehicle_opex,
)
from savings.opex.get_fixed_costs import get_fixed_costs
from savings.opex.get_solar_savings import get_solar_savings


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


def _get_total_opex(household: Household, period: PeriodEnum) -> float:

    energy_needs = get_total_energy_needs(household, period)

    appliance_opex = _get_total_appliance_energy(household, period)
    vehicle_opex = get_vehicle_opex(household.vehicles, period)
    other_opex = get_other_appliances_opex_per_period(period)
    fixed_costs = get_fixed_costs(household, period)
    solar_savings = get_solar_savings(
        energy_needs, household.solar, household.battery, household.location, period
    )

    return appliance_opex + vehicle_opex + other_opex + fixed_costs - solar_savings


def _get_total_appliance_energy(household: Household, period: PeriodEnum):
    return (
        get_energy_per_period(household.space_heating, SPACE_HEATING_INFO, period)
        + get_energy_per_period(household.water_heating, WATER_HEATING_INFO, period)
        + get_energy_per_period(household.cooktop, COOKTOP_INFO, period)
    )


# Solar savings

# TODO: Ideally we would calculate the exact house needs based on the appliances listed in survey responses
# plus extra appliances above, then calculate the actual consumption from grid, generation from solar, and amount sold to grid.
# But as a quick proxy, we're going to just take the average solar savings
# and apply it to all households in the dataset.

# Average total energy needs of home
# TODO: The below is wrong, just use the direct results from the sheet
# Use value from "Full home"!E25, when C8 Vehicle number is 0 and C12 Solar size is 5 kW
TOTAL_ELECTRICITY_NEEDS = 13.5  # kWh per day
POWER_BILL_NO_SOLAR = (
    TOTAL_ELECTRICITY_NEEDS
    * COST_PER_FUEL_KWH_TODAY[FuelTypeEnum.ELECTRICITY]["volume_rate"]
)

# How much of the avg total energy needs can solar provide (free)?
SOLAR_SELF_CONSUMPTION_ON_APPLIANCES = 0.5  # C14
GENERATED_FROM_SOLAR = TOTAL_ELECTRICITY_NEEDS * SOLAR_SELF_CONSUMPTION_ON_APPLIANCES

# How much do you need from the grid, and how much does it cost?
CONSUMED_FROM_GRID = TOTAL_ELECTRICITY_NEEDS - GENERATED_FROM_SOLAR  # kWh/day
POWER_BILL_WITH_SOLAR = (
    CONSUMED_FROM_GRID
    * COST_PER_FUEL_KWH_TODAY[FuelTypeEnum.ELECTRICITY]["volume_rate"]
)

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
