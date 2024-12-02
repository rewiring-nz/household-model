from typing import List
from constants.machines.vehicles import RUCS
from constants.solar import SOLAR_FEEDIN_TARIFF_2024, SOLAR_FEEDIN_TARIFF_AVG_15_YEARS
from constants.utils import DAYS_PER_YEAR, WEEKS_PER_YEAR, PeriodEnum
from openapi_client.models.vehicle import Vehicle
from params import (
    OPERATIONAL_LIFETIME,
)
from constants.fuel_stats import (
    COST_PER_FUEL_KWH_AVG_15_YEARS,
    COST_PER_FUEL_KWH_TODAY,
    FuelTypeEnum,
)

from openapi_client.models import (
    Household,
    Opex,
    OpexValues,
)
from savings.energy.get_machine_energy import (
    get_total_energy_needs,
)
from savings.energy.get_other_energy_consumption import get_other_energy_consumption
from savings.opex.get_fixed_costs import get_fixed_costs
from savings.energy.get_electricity_consumption import (
    ElectricityConsumption,
    get_electricity_consumption,
)
from savings.energy.get_other_energy_consumption import (
    OtherEnergyConsumption,
    get_other_energy_consumption,
)
from savings.opex.get_other_energy_costs import get_other_energy_costs
from utils.scale_daily_to_period import scale_daily_to_period


def calculate_opex(
    current_household: Household, electrified_household: Household
) -> Opex:
    print(f"\n\n\n======= OPEX =======")

    # Weekly
    print(f"\n\n\nWEEKLY")
    print(f"\nBefore\n")
    weekly_before = _get_total_opex(current_household, PeriodEnum.WEEKLY)
    print(f"\nAfter\n")
    weekly_after = _get_total_opex(electrified_household, PeriodEnum.WEEKLY)

    print(f"\n\n\nYEARLY")
    # Yearly
    print(f"\nBefore\n")
    yearly_before = _get_total_opex(current_household, PeriodEnum.YEARLY)
    print(f"\nAfter\n")
    yearly_after = _get_total_opex(electrified_household, PeriodEnum.YEARLY)

    print(f"\n\n\nLIFETIME")
    # Operational lifetime
    print(f"\nBefore\n")
    lifetime_before = _get_total_opex(
        current_household, PeriodEnum.OPERATIONAL_LIFETIME
    )
    print(f"\nAfter\n")
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
    electricity_consumption = get_electricity_consumption(
        energy_needs, household.solar, household.battery, household.location, period
    )
    other_energy_consumption = get_other_energy_consumption(energy_needs)
    total_bills = get_total_bills(
        household, electricity_consumption, other_energy_consumption, period
    )
    return total_bills


def get_total_bills(
    household: Household,
    electricity_consumption: ElectricityConsumption,
    other_energy_consumption: OtherEnergyConsumption,
    period: PeriodEnum,
) -> float:
    # Costs
    grid_volume_costs = get_grid_volume_cost(
        electricity_consumption["consumed_from_grid"],
        electricity_consumption["consumed_from_battery"],
        period,
    )
    print("\n\ngrid_volume_costs: ", grid_volume_costs)

    other_energy_costs = get_other_energy_costs(other_energy_consumption, period)
    print("other_energy_costs: ", other_energy_costs)

    fixed_costs = get_fixed_costs(household, period)
    print("fixed_costs: ", fixed_costs)

    rucs = get_rucs(household.vehicles, period)
    print("rucs: ", rucs)

    # Savings
    revenue_from_solar_export = get_solar_feedin_tariff(
        electricity_consumption["exported_to_grid"], period
    )
    print("revenue_from_solar_export: ", revenue_from_solar_export)
    print("\n\n")

    return (
        grid_volume_costs
        + other_energy_costs
        + fixed_costs
        + rucs
        - revenue_from_solar_export
    )


def get_grid_volume_cost(
    e_consumed_from_grid: float, e_from_battery: float, period: PeriodEnum
) -> float:
    grid_price = get_effective_grid_price(e_consumed_from_grid, e_from_battery, period)
    return e_consumed_from_grid * grid_price


def get_effective_grid_price(
    e_consumed_from_grid: float, e_from_battery: float, period: PeriodEnum
) -> float:
    """Get the effective grid price

    Adjusts the grid price based on what proportion of the energy consumed from the grid
    would have been bought off-peak by the battery versus bought at the volume rate.

    If period is DAILY, WEEKLY or YEARLY, will use 2024 prices.
    If period is OPERATIONAL_LIFETIME, will use real prices averaged over next 15 years (takes inflation into account).

    Args:
        e_consumed_from_grid (float): energy consumed from the grid in kWh
        e_from_battery (float): energy consumed from the battery in kWh
        period (PeriodEnum): the period for which this calculation is over

    Returns:
        float: the effective grid price
    """
    # TODO: Unit test
    costs = (
        COST_PER_FUEL_KWH_AVG_15_YEARS
        if period == PeriodEnum.OPERATIONAL_LIFETIME
        else COST_PER_FUEL_KWH_TODAY
    )
    grid_price = costs[FuelTypeEnum.ELECTRICITY]["volume_rate"]
    if e_from_battery > 0:
        if e_from_battery >= e_consumed_from_grid:
            # All energy is from the battery, which could be charged at off peak price
            grid_price = costs[FuelTypeEnum.ELECTRICITY]["off_peak"]
        if e_from_battery < e_consumed_from_grid:
            # A proportion of the energy consumed from the grid was bought at off peak price
            percent_of_consumed_from_battery = e_from_battery / e_consumed_from_grid
            grid_price = (
                costs[FuelTypeEnum.ELECTRICITY]["off_peak"]
                * percent_of_consumed_from_battery
            ) + (
                costs[FuelTypeEnum.ELECTRICITY]["volume_rate"]
                * (1 - percent_of_consumed_from_battery)
            )
    return grid_price


def get_rucs(vehicles: List[Vehicle], period: PeriodEnum = PeriodEnum.DAILY) -> float:
    """Calculates the RUCs for a list of vehicles weighted by kms per year

    Args:
        vehicles (List[Vehicle]): the list of vehicles
        period (PeriodEnum, optional): the period over which to calculate the RUCs.

    Returns:
        float: total NZD emitted from vehicles over given period to 2dp
    """
    total_rucs_daily = 0
    for vehicle in vehicles:
        rucs_daily = (
            RUCS[vehicle.fuel_type]  # $/yr/1000km
            * vehicle.kms_per_week  # km/wk
            * WEEKS_PER_YEAR  # wk/yr
            / 1000
            / DAYS_PER_YEAR  # days/yr
        )
        # Convert to given period
        total_rucs_daily += rucs_daily
    total_rucs = scale_daily_to_period(total_rucs_daily, period)
    return round(total_rucs, 2)


def get_solar_feedin_tariff(e_exported: float, period: PeriodEnum) -> float:
    if PeriodEnum.OPERATIONAL_LIFETIME:
        return e_exported * SOLAR_FEEDIN_TARIFF_AVG_15_YEARS
    return e_exported * SOLAR_FEEDIN_TARIFF_2024
