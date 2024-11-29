from dataclasses import dataclass
from typing import Dict, Tuple

from constants.battery import (
    BATTERY_AVG_DEGRADED_PERFORMANCE_15_YRS,
    BATTERY_CYCLES_PER_DAY,
    BATTERY_LOSSES,
)
from constants.fuel_stats import FuelTypeEnum
from constants.solar import (
    SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS,
    SOLAR_CAPACITY_FACTOR,
    SOLAR_SELF_CONSUMPTION_APPLIANCES,
    SOLAR_SELF_CONSUMPTION_OTHER_APPLIANCES,
    SOLAR_SELF_CONSUMPTION_VEHICLES,
)
from openapi_client.models.battery import Battery
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from constants.utils import DAYS_PER_YEAR, PeriodEnum
from params import OPERATIONAL_LIFETIME
from savings.energy.get_machine_energy import MachineEnergyNeeds
from utils.scale_daily_to_period import scale_daily_to_period
from utils.sum_dicts import sum_dicts


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

    print(f"\n\n PERIOD: {period}")
    # Energy in kWh per period

    # Total energy needs # TODO remove this, don't need it
    e_needed_total: Dict[FuelTypeEnum, float] = sum_dicts()
    print(f"e_needed_total: {energy_needs}")

    # Energy needs met by solar
    e_generated_from_solar = get_e_generated_from_solar(solar, location, period)
    e_consumed_from_solar, e_needs_remaining = get_e_consumed_from_solar(
        e_generated_from_solar, energy_needs
    )
    print(f"e_generated_from_solar: {e_generated_from_solar}")
    print(f"e_consumed_from_solar: {e_consumed_from_solar}")

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
    if e_consumed_from_grid < 0:
        e_consumed_from_grid = 0

    # Excess generated energy exported
    e_exported = e_consumed_from_grid + e_generated_from_solar - e_needed_total
    print(f"e_consumed_from_battery: {e_consumed_from_battery}")
    print(f"e_consumed_from_grid: {e_consumed_from_grid}")
    print(f"total consumed from household: {e_consumed_from_grid}")
    print(f"e_exported: {e_exported}")

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
    if solar.has_solar is True and solar.size is not None and solar.size > 0:
        e_daily = (
            solar.size
            * SOLAR_CAPACITY_FACTOR.get(location)
            * SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS
            * 24  # hours per day
        )
    return scale_daily_to_period(e_daily, period)


def get_e_consumed_from_solar(
    e_generated_from_solar: float,
    e_needs: MachineEnergyNeeds,
) -> Tuple[float, MachineEnergyNeeds]:
    """Calculate energy consumed from solar
    All arguments should be energy given or needed over the same period of time.

    Args:
        e_generated_from_solar (float): kWh generated from solar
        e_needs (MachineEnergyNeeds): kWh required per fuel type by machine types

    Returns:
        float: kWh remaining from the generated solar
        MachineEnergyNeeds: kWh consumed from the generated solar
        MachineEnergyNeeds: kWh remaining to be met by other sources
    """
    e_consumed_from_solar = (
        SOLAR_SELF_CONSUMPTION_APPLIANCES * e_needs.appliances
        + SOLAR_SELF_CONSUMPTION_VEHICLES * e_needs.vehicles
        + SOLAR_SELF_CONSUMPTION_OTHER_APPLIANCES * e_needs.other_appliances
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
            capacity_per_day * DAYS_PER_YEAR * OPERATIONAL_LIFETIME
        )

    # If the energy remaining from generation after self-consumption is less than the battery's capacity, battery stores all the remaining energy
    if e_remaining_after_self_consumption < e_battery_storage_capacity:
        return e_remaining_after_self_consumption

    # If there is more energy remaining than the capacity, the battery is filled to capacity
    return e_battery_storage_capacity
