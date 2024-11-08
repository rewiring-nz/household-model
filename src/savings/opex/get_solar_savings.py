from multiprocessing import Value
from typing import Optional, Union

from pydantic import StrictFloat, StrictInt
from constants.battery import (
    BATTERY_AVG_DEGRADED_PERFORMANCE_15_YRS,
    BATTERY_CYCLES_PER_DAY,
    BATTERY_LOSSES,
)
from constants.fuel_stats import (
    COST_PER_FUEL_KWH_AVG_15_YEARS,
    FIXED_COSTS_PER_YEAR_AVG_15_YEARS,
    FuelTypeEnum,
)
from constants.solar import (
    SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS,
    SOLAR_CAPACITY_FACTOR,
    SOLAR_FEEDIN_TARIFF_2024,
    SOLAR_SELF_CONSUMPTION_APPLIANCES,
    SOLAR_SELF_CONSUMPTION_VEHICLES,
)
from openapi_client.models.battery import Battery
from openapi_client.models.household import Household
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from constants.utils import DAYS_PER_YEAR, HOURS_PER_YEAR, PeriodEnum
from utils.scale_daily_to_period import scale_daily_to_period


def get_solar_savings(
    solar: Solar,
    battery: Battery,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    # TODO
    # if installing solar
    # substract AVG_SAVINGS_FROM_SOLAR_0_VEHICLES_5KWH or AVG_SAVINGS_FROM_SOLAR_2_VEHICLES_7KWH but dynamic to solar size
    # check if these apply even without battery, and what the impact of the battery is
    if not solar.has_solar or solar.size is None:
        return 0

    # kWh per year
    e_needed_by_appliances = 80  # TODO
    e_needed_by_vehicles = 50  # TODO
    e_needed_total = e_needed_by_appliances + e_needed_by_vehicles

    e_generated_from_solar = get_e_generated_from_solar(solar.size)
    e_consumed_from_solar = get_e_consumed_from_solar(
        e_generated_from_solar, e_needed_by_appliances, e_needed_by_vehicles
    )

    e_from_battery = 0
    if battery.has_battery and battery.capacity is not None:
        # electricity stored in battery, then consumed or exported
        e_from_battery = get_e_consumed_from_battery(
            battery.capacity, e_generated_from_solar, e_consumed_from_solar
        )

    e_consumed_from_grid = e_needed_total - e_consumed_from_solar - e_from_battery
    e_exported = e_consumed_from_grid + e_generated_from_solar - e_needed_total
    # per year
    return e_exported


def get_e_generated_from_solar(solar_size: float, location: LocationEnum) -> float:
    """Calculate energy generated from solar

    Args:
        solar_size (float): The size of the solar panel system in kW, >= 0
        location (LocationEnum): The location around NZ which determines the solar capacity

    Returns:
        float: energy generated per year in kWh
    """
    return (
        solar_size
        * SOLAR_CAPACITY_FACTOR.get(location)
        * HOURS_PER_YEAR
        * SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS
    )


def get_e_consumed_from_solar(
    e_generated_from_solar: float,
    e_needed_by_appliances: float,
    e_needed_by_vehicles: float,
) -> float:
    """Calculate energy consumed from solar

    Args:
        e_generated_from_solar (float): kWh generated from solar in a year
        e_needed_by_appliances (float): kWh required by appliances in a year
        e_needed_by_vehicles (float): kWh required by vehicles in a year

    Returns:
        float: kWh consumed from the generated solar in one year
    """
    e_consumed_from_solar = (
        SOLAR_SELF_CONSUMPTION_APPLIANCES * e_needed_by_appliances
        + SOLAR_SELF_CONSUMPTION_VEHICLES * e_needed_by_vehicles
    )
    if e_consumed_from_solar > e_generated_from_solar:
        return e_generated_from_solar
    return e_consumed_from_solar


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


def get_e_consumed_from_battery(
    battery_capacity: float, e_generated_from_solar: float, e_consumed_from_solar: float
) -> float:
    """Calculate the energy stored and consumed from the battery

    This essentially removes the need to buy this amount of energy from the grid at peak prices,
    allowing the household to make the most of off-peak grid prices, assuming that they take
    advantage of such spot prices.

    Args:
        battery_capacity (float): battery nameplate capacity in kWh/cycle
        e_generated_from_solar (float): the electricity in kWh/year generated from solar
        e_consumed_from_solar (float): the electricity in kWh/year consumed from the solar. Should be equal to or less than e_generated_from_solar.

    Returns:
        float: _description_
    """
    if e_consumed_from_solar > e_generated_from_solar:
        raise ValueError("Energy consumed is higher than energy generated.")

    e_remaining_after_self_consumption = e_generated_from_solar - e_consumed_from_solar
    e_battery_storage_capacity = (
        battery_capacity  # kWh/cycle
        * BATTERY_CYCLES_PER_DAY  # cycle/day
        * BATTERY_AVG_DEGRADED_PERFORMANCE_15_YRS
        * (1 - BATTERY_LOSSES)
        * DAYS_PER_YEAR  # day/yr
    )  # kWh/yr

    # If the energy remaining from generation after self-consumption is less than the battery's capacity, battery stores all the remaining energy
    if e_remaining_after_self_consumption < e_battery_storage_capacity:
        return e_remaining_after_self_consumption

    # If there is more energy remaining than the capacity, the battery is filled to capacity
    return e_battery_storage_capacity
