from typing import Dict, Tuple, TypedDict

from constants.battery import (
    BATTERY_AVG_DEGRADED_PERFORMANCE_15_YRS,
    BATTERY_CYCLES_PER_DAY,
    BATTERY_LOSSES,
)
from constants.fuel_stats import FuelTypeEnum
from constants.solar import (
    MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE,
    SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS,
    SOLAR_CAPACITY_FACTOR,
)
from openapi_client.models.battery import Battery
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from constants.utils import DAYS_PER_YEAR, PeriodEnum
from params import OPERATIONAL_LIFETIME
from savings.energy.get_machine_energy import MachineEnergyNeeds
from utils.scale_daily_to_period import scale_daily_to_period


class ElectricityConsumption(TypedDict):
    consumed_from_solar: float
    consumed_from_battery: float
    consumed_from_grid: float
    exported_to_grid: float


def get_electricity_consumption(
    energy_needs: MachineEnergyNeeds,
    solar: Solar,
    battery: Battery,
    location: LocationEnum,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> ElectricityConsumption:

    print(f"\n\n PERIOD: {period}")
    # Energy in kWh per period

    # Energy needs met by solar
    e_generated_from_solar = get_e_generated_from_solar(solar, location, period)
    print(f"e_generated_from_solar: {e_generated_from_solar}")

    e_consumed_from_solar, e_generated_remaining, e_needs_remaining = (
        get_e_consumed_from_solar(e_generated_from_solar, energy_needs)
    )
    print(f"e_consumed_from_solar: {e_consumed_from_solar}")
    print(f"e_needs_remaining: {e_needs_remaining}")

    # Energy needs met by battery
    e_consumed_from_battery = 0
    # We don't consider self-consumption rates for battery, so we can combine the electricity consumed from solar by different machines at this stage. In future, we may wish to be more sophisticated about how certain machines pull more from the battery due to usage patterns.
    total_e_consumed_from_solar = sum_energy_for_fuel_type(
        e_consumed_from_solar, FuelTypeEnum.ELECTRICITY
    )
    total_e_needs_remaining = sum_energy_for_fuel_type(
        e_needs_remaining, FuelTypeEnum.ELECTRICITY
    )
    if battery.has_battery and battery.capacity is not None:
        # electricity stored in battery, then consumed or exported
        e_consumed_from_battery = get_e_consumed_from_battery(
            battery.capacity,
            e_generated_from_solar,
            total_e_consumed_from_solar,
            period,
        )

    # Energy needs met by grid
    total_e_consumed_from_grid = total_e_needs_remaining - e_consumed_from_battery

    if total_e_consumed_from_grid < 0:
        total_e_consumed_from_grid = 0

    total_e_needs = sum_energy_for_fuel_type(energy_needs, FuelTypeEnum.ELECTRICITY)
    # Excess generated energy exported
    e_exported = total_e_consumed_from_grid + e_generated_from_solar - total_e_needs
    print(f"e_consumed_from_battery: {e_consumed_from_battery}")
    print(f"total_e_consumed_from_grid: {total_e_consumed_from_grid}")
    print(f"total_e_consumed_from_grid: {total_e_consumed_from_grid}")
    print(f"e_exported: {e_exported}")

    electricity_consumption: ElectricityConsumption = {
        "consumed_from_solar": total_e_consumed_from_solar,
        "consumed_from_battery": e_consumed_from_battery,
        "consumed_from_grid": total_e_consumed_from_grid,
        "exported_to_grid": e_exported,
    }
    return electricity_consumption


def sum_energy_for_fuel_type(
    e_needs: MachineEnergyNeeds, fuel_type: FuelTypeEnum
) -> float:
    # Sums the energy needs across categories for a given fuel type
    e = 0
    categories = list(MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE.keys())
    for cat in categories:
        if e_needs.get(cat) is not None:
            e += sum(
                need * MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE[cat]
                for fuel, need in e_needs.get(cat).items()
                if fuel == fuel_type
            )
    return e


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


def _get_max_e_consumed_from_solar(e_needs: MachineEnergyNeeds) -> MachineEnergyNeeds:
    categories = list(MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE.keys())
    return {
        cat: {
            FuelTypeEnum.ELECTRICITY: e_needs[cat][FuelTypeEnum.ELECTRICITY]
            * MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE[cat]
        }
        for cat in categories
        if cat in e_needs
    }


def _calculate_e_consumed_from_solar_with_deficit(
    e_demand: float, total_demand: float, total_deficit: float
) -> float:
    proportion_of_demand = e_demand / total_demand
    deficit_portion = total_deficit * proportion_of_demand
    return e_demand - deficit_portion


def get_e_consumed_from_solar(
    e_generated_from_solar: float,
    e_needs: MachineEnergyNeeds,
) -> Tuple[MachineEnergyNeeds, float, MachineEnergyNeeds]:
    """Calculate energy consumed from solar
    All arguments should be energy given or needed over the same period of time.

    Args:
        e_generated_from_solar (float): kWh generated from solar
        e_needs (MachineEnergyNeeds): kWh required per fuel type by machine types

    Returns:
        Tuple[MachineEnergyNeeds, float, MachineEnergyNeeds]: kWh consumed from the generated solar, kWh remaining from the generated solar, kWh remaining to be met by other sources
    """
    # Calculate electric needs across categories
    categories = list(MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE.keys())

    # Default to meeting all electricity needs at self-consumption rate
    e_consumed_from_solar = _get_max_e_consumed_from_solar(e_needs)

    # Calculate total maximum energy consumed from solar at self-consumption rate
    total_max_consumed_from_solar = sum(
        e_needs_for_cat[FuelTypeEnum.ELECTRICITY]
        for e_needs_for_cat in e_consumed_from_solar.values()
    )

    # If all electric needs can be met with solar, some solar remains, energy needs remain based on self-consumption
    if total_max_consumed_from_solar <= e_generated_from_solar:
        remaining_solar = e_generated_from_solar - total_max_consumed_from_solar

    # If not enough solar generation to meet all electric needs,
    # Distribute the deficit across categories, proportional to self-consumed energy size
    if total_max_consumed_from_solar > e_generated_from_solar:
        deficit = total_max_consumed_from_solar - e_generated_from_solar
        for cat in categories:
            e_consumed_from_solar[cat][FuelTypeEnum.ELECTRICITY] = (
                _calculate_e_consumed_from_solar_with_deficit(
                    e_consumed_from_solar[cat][FuelTypeEnum.ELECTRICITY],
                    total_max_consumed_from_solar,
                    deficit,
                )
            )
        remaining_solar = 0

    e_needs_remaining = {
        cat: {
            fuel_type: (
                # Calculate remaining electricity need after solar consumption
                e_needs[cat][fuel_type] - e_consumed_from_solar[cat][fuel_type]
                if fuel_type == FuelTypeEnum.ELECTRICITY
                # Other fuel types stay as is
                else val
            )
            for fuel_type, val in e_needs[cat].items()
        }
        for cat in categories
        if cat in e_needs
    }
    return e_consumed_from_solar, remaining_solar, e_needs_remaining


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
