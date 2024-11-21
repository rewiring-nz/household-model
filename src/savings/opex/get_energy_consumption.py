from dataclasses import dataclass

from constants.battery import (
    BATTERY_AVG_DEGRADED_PERFORMANCE_15_YRS,
    BATTERY_CYCLES_PER_DAY,
    BATTERY_LOSSES,
)
from constants.fuel_stats import (
    COST_PER_FUEL_KWH_AVG_15_YEARS,
    FuelTypeEnum,
)
from constants.solar import (
    SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS,
    SOLAR_CAPACITY_FACTOR,
    SOLAR_FEEDIN_TARIFF_2024,
    SOLAR_OPERATIONAL_LIFETIME_YRS,
    SOLAR_SELF_CONSUMPTION_APPLIANCES,
    SOLAR_SELF_CONSUMPTION_VEHICLES,
)
from openapi_client.models.battery import Battery
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from constants.utils import DAYS_PER_YEAR, HOURS_PER_YEAR, PeriodEnum
from savings.energy.get_machine_energy import MachineEnergyNeeds
from utils.scale_daily_to_period import scale_daily_to_period


@dataclass
class EnergyConsumption:
    consumed_from_solar: float
    consumed_from_battery: float
    consumed_from_grid: float
    exported_to_grid: float


def get_energy_consumption(
    energy_needs: MachineEnergyNeeds,
    solar: Solar,
    battery: Battery,
    location: LocationEnum,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:

    # Energy in kWh per period

    # Total energy needs
    e_needed_total = energy_needs.appliances + energy_needs.vehicles

    # Energy needs met by solar
    e_generated_from_solar = get_e_generated_from_solar(solar, location, period)
    e_consumed_from_solar = get_e_consumed_from_solar(
        e_generated_from_solar, energy_needs.appliances, energy_needs.vehicles
    )

    # Energy needs met by battery
    e_consumed_from_battery = 0
    if battery.has_battery and battery.capacity is not None:
        # electricity stored in battery, then consumed or exported
        e_consumed_from_battery = get_e_consumed_from_battery(
            battery.capacity, e_generated_from_solar, e_consumed_from_solar, period
        )

    # Energy needs met by grid
    e_consumed_from_grid = (
        e_needed_total - e_consumed_from_solar - e_consumed_from_battery
    )

    # Excess generated energy exported
    e_exported = e_consumed_from_grid + e_generated_from_solar - e_needed_total

    return EnergyConsumption(
        consumed_from_solar=e_consumed_from_solar,
        consumed_from_battery=e_consumed_from_battery,
        consumed_from_grid=e_consumed_from_grid,
        exported_to_grid=e_exported,
    )


def get_e_generated_from_solar(
    solar: Solar, location: LocationEnum, period: PeriodEnum = PeriodEnum.YEARLY
) -> float:
    """Calculate energy generated from solar

    Args:
        solar (Solar): Information about the solar panel system
        location (LocationEnum): The location around NZ which determines the solar capacity
        period (PeriodEnum): the period over which to calculate generation

    Returns:
        float: energy generated per year in kWh
    """
    e_daily = 0
    if solar.size is not None and solar.size > 0:
        e_daily = (
            solar.size
            * SOLAR_CAPACITY_FACTOR.get(location)
            * SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS
            * 24  # hours per day
        )
    return scale_daily_to_period(e_daily, period, SOLAR_OPERATIONAL_LIFETIME_YRS)


def get_e_consumed_from_solar(
    e_generated_from_solar: float,
    e_needed_by_appliances: float,
    e_needed_by_vehicles: float,
) -> float:
    """Calculate energy consumed from solar
    All arguments should be energy given or needed over the same period of time.

    Args:
        e_generated_from_solar (float): kWh generated from solar
        e_needed_by_appliances (float): kWh required by appliances
        e_needed_by_vehicles (float): kWh required by vehicles

    Returns:
        float: kWh consumed from the generated solar
    """
    e_consumed_from_solar = (
        SOLAR_SELF_CONSUMPTION_APPLIANCES * e_needed_by_appliances
        + SOLAR_SELF_CONSUMPTION_VEHICLES * e_needed_by_vehicles
    )
    if e_consumed_from_solar > e_generated_from_solar:
        return e_generated_from_solar
    return e_consumed_from_solar


def get_e_consumed_from_battery(
    battery_capacity: float,
    e_generated_from_solar: float,
    e_consumed_from_solar: float,
    period: PeriodEnum = PeriodEnum.YEARLY,
) -> float:
    """Calculate the energy stored and consumed from the battery

    This essentially removes the need to buy this amount of energy from the grid at peak prices,
    allowing the household to make the most of off-peak grid prices, assuming that they take
    advantage of such spot prices.

    Args:
        battery_capacity (float): battery nameplate capacity in kWh/cycle
        e_generated_from_solar (float): the electricity in kWh/year generated from solar
        e_consumed_from_solar (float): the electricity in kWh/year consumed from the solar. Should be equal to or less than e_generated_from_solar.
        period (PeriodEnum): the period over which to calculate

    Returns:
        float: energy in kWh per period
    """
    if e_consumed_from_solar > e_generated_from_solar:
        raise ValueError("Energy consumed is higher than energy generated.")

    e_remaining_after_self_consumption = e_generated_from_solar - e_consumed_from_solar

    # TODO: put this into separate function
    capacity_per_day = (
        battery_capacity  # kWh/cycle
        * BATTERY_CYCLES_PER_DAY  # cycle/day
        * BATTERY_AVG_DEGRADED_PERFORMANCE_15_YRS
        * (1 - BATTERY_LOSSES)
    )  # kWh/day
    e_battery_storage_capacity = capacity_per_day
    if period == PeriodEnum.WEEKLY:
        e_battery_storage_capacity = capacity_per_day * 7
    if period == PeriodEnum.YEARLY:
        e_battery_storage_capacity = capacity_per_day * DAYS_PER_YEAR
    if period == PeriodEnum.OPERATIONAL_LIFETIME:
        e_battery_storage_capacity = (
            capacity_per_day * DAYS_PER_YEAR * SOLAR_OPERATIONAL_LIFETIME_YRS
        )

    # If the energy remaining from generation after self-consumption is less than the battery's capacity, battery stores all the remaining energy
    if e_remaining_after_self_consumption < e_battery_storage_capacity:
        return e_remaining_after_self_consumption

    # If there is more energy remaining than the capacity, the battery is filled to capacity
    return e_battery_storage_capacity


def get_total_bills(
    has_battery: bool, e_consumed_from_grid: float, e_from_battery: float
) -> float:
    grid_volume_costs = get_electricity_opex(
        has_battery, e_consumed_from_grid, e_from_battery
    )
    # grid_fixed_costs = TODO
    # revenue_from_solar_export = get_solar_feedin_tariff(e_exported)
    rucs = get_rucs()
    return grid_volume_costs + rucs
    # return grid_volume_costs + grid_fixed_costs + rucs - revenue_from_solar_export


def get_rucs():
    pass


def get_electricity_opex(
    has_battery: bool, e_consumed_from_grid: float, e_from_battery: float
) -> float:
    grid_price = get_effective_grid_price(
        has_battery, e_consumed_from_grid, e_from_battery
    )
    return e_consumed_from_grid * grid_price


def get_effective_grid_price(
    has_battery: bool, e_consumed_from_grid: float, e_from_battery: float
) -> float:
    """Get the effective grid price

    Adjusts the grid price based on what proportion of the energy consumed from the grid
    would have been bought off-peak by the battery versus bought at the volume rate.

    Args:
        has_battery (bool): whether the household has a battery
        e_consumed_from_grid (float): energy consumed from the grid in kWh
        e_from_battery (float): energy consumed from the battery in kWh

    Returns:
        float: the effective grid price
    """
    grid_price = COST_PER_FUEL_KWH_AVG_15_YEARS[FuelTypeEnum.ELECTRICITY]["volume_rate"]
    if has_battery:
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


def get_solar_feedin_tariff(e_exported: float) -> float:
    return e_exported * SOLAR_FEEDIN_TARIFF_2024
