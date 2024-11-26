from typing import List
from constants.machines.vehicles import RUCS
from constants.solar import SOLAR_FEEDIN_TARIFF_2024
from constants.utils import DAYS_PER_YEAR, WEEKS_PER_YEAR, PeriodEnum
from openapi_client.models.vehicle import Vehicle
from params import (
    OPERATIONAL_LIFETIME,
)
from constants.fuel_stats import COST_PER_FUEL_KWH_AVG_15_YEARS, FuelTypeEnum

from openapi_client.models import (
    Household,
    Opex,
    OpexValues,
)
from savings.energy.get_machine_energy import (
    get_total_energy_needs,
)
from savings.opex.get_fixed_costs import get_fixed_costs
from savings.energy.get_energy_consumption import (
    EnergyConsumption,
    get_energy_consumption,
)
from utils.scale_daily_to_period import scale_daily_to_period


def calculate_opex(
    current_household: Household, electrified_household: Household
) -> Opex:

    # Weekly
    print(f"\n\nWEEKLY")
    print(f"\nBefore")
    weekly_before = _get_total_opex(current_household, PeriodEnum.WEEKLY)
    print(f"\nAfter")
    weekly_after = _get_total_opex(electrified_household, PeriodEnum.WEEKLY)

    print(f"\n\nYEARLY")
    # Yearly
    print(f"\nBefore")
    yearly_before = _get_total_opex(current_household, PeriodEnum.YEARLY)
    print(f"\nAfter")
    yearly_after = _get_total_opex(electrified_household, PeriodEnum.YEARLY)

    print(f"\n\nLIFETIME")
    # Operational lifetime
    print(f"\nBefore")
    lifetime_before = _get_total_opex(
        current_household, PeriodEnum.OPERATIONAL_LIFETIME
    )
    print(f"\nAfter")
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
    energy_consumption = get_energy_consumption(
        energy_needs, household.solar, household.battery, household.location, period
    )
    total_bills = get_total_bills(household, energy_consumption, period)
    return total_bills


def get_total_bills(
    household: Household, energy_consumption: EnergyConsumption, period: PeriodEnum
) -> float:
    # Costs
    grid_volume_costs = get_grid_volume_cost(
        energy_consumption.consumed_from_grid, energy_consumption.consumed_from_battery
    )
    fixed_costs = get_fixed_costs(household, period)
    rucs = get_rucs(household.vehicles, period)

    # Savings
    revenue_from_solar_export = get_solar_feedin_tariff(
        energy_consumption.exported_to_grid
    )

    return grid_volume_costs + fixed_costs + rucs - revenue_from_solar_export


def get_grid_volume_cost(e_consumed_from_grid: float, e_from_battery: float) -> float:
    grid_price = get_effective_grid_price(e_consumed_from_grid, e_from_battery)
    return e_consumed_from_grid * grid_price


def get_effective_grid_price(
    e_consumed_from_grid: float, e_from_battery: float
) -> float:
    """Get the effective grid price

    Adjusts the grid price based on what proportion of the energy consumed from the grid
    would have been bought off-peak by the battery versus bought at the volume rate.
    Uses real grid prices averaged over next 15 years (takes inflation into account).

    Args:
        e_consumed_from_grid (float): energy consumed from the grid in kWh
        e_from_battery (float): energy consumed from the battery in kWh

    Returns:
        float: the effective grid price
    """
    grid_price = COST_PER_FUEL_KWH_AVG_15_YEARS[FuelTypeEnum.ELECTRICITY]["volume_rate"]
    if e_from_battery > 0:
        if e_from_battery >= e_consumed_from_grid:
            # All energy is from the battery, which could be charged at off peak price
            grid_price = COST_PER_FUEL_KWH_AVG_15_YEARS[FuelTypeEnum.ELECTRICITY][
                "off_peak"
            ]
        if e_from_battery < e_consumed_from_grid:
            # A proportion of the energy consumed from the grid was bought at off peak price
            percent_of_consumed_from_battery = e_from_battery / e_consumed_from_grid
            grid_price = (
                COST_PER_FUEL_KWH_AVG_15_YEARS[FuelTypeEnum.ELECTRICITY]["off_peak"]
                * percent_of_consumed_from_battery
            ) + (
                COST_PER_FUEL_KWH_AVG_15_YEARS[FuelTypeEnum.ELECTRICITY]["volume_rate"]
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


def get_solar_feedin_tariff(e_exported: float) -> float:
    # TODO: Use average prices over 15 years if period is operational lifetime
    return e_exported * SOLAR_FEEDIN_TARIFF_2024
