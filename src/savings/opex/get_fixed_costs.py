from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.household import Household
from openapi_client.models.space_heating_enum import SpaceHeatingEnum

from constants.fuel_stats import (
    FIXED_COSTS_PER_YEAR_2024,
    FIXED_COSTS_PER_YEAR_AVG_15_YEARS,
    FuelTypeEnum,
)
from constants.utils import DAYS_PER_YEAR, PeriodEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from utils.scale_daily_to_period import scale_daily_to_period


def get_fixed_costs(
    household: Household,
    period: PeriodEnum = PeriodEnum.DAILY,
    ignore_lpg_if_ngas_present: bool = False,
) -> float:
    """Calculate fixed utility connection costs for a household.

    Computes the fixed costs paid for utility connections (electricity, natural gas, and LPG)
    based on the household's energy usage profile. Electricity costs are always included
    since we assume the house remains connected to the grid for other devices.

    Args:
        household (Household): object containing machine & energy type information
        period (PeriodEnum, optional): time period for cost calculation. (default: PeriodEnum.DAILY)
        ignore_lpg_if_ngas_present: If True, ignore LPG costs when natural gas is present,
            assuming LPG usage is minimal (e.g., outdoor BBQ) (default: False)

    Returns:
        float: fixed costs for the specified period
    """
    daily_costs = _get_daily_cost(FuelTypeEnum.ELECTRICITY, period)

    uses_natural_gas = any(
        [
            household.space_heating == SpaceHeatingEnum.GAS,
            household.water_heating == WaterHeatingEnum.GAS,
            household.cooktop == CooktopEnum.GAS,
        ]
    )
    if uses_natural_gas:
        daily_costs += _get_daily_cost(FuelTypeEnum.NATURAL_GAS, period)

    uses_lpg = any(
        [
            household.space_heating == SpaceHeatingEnum.LPG,
            household.water_heating == WaterHeatingEnum.LPG,
            household.cooktop == CooktopEnum.LPG,
        ]
    )
    if uses_lpg and not (ignore_lpg_if_ngas_present and uses_natural_gas):
        daily_costs += _get_daily_cost(FuelTypeEnum.LPG, period)

    return scale_daily_to_period(daily_costs, period)


def _get_daily_cost(fuel_type: FuelTypeEnum, period: PeriodEnum) -> float:
    """
    Helper to get daily cost for a fuel type
    Period is used to figure out what pricing to use.
    """
    costs = (
        FIXED_COSTS_PER_YEAR_AVG_15_YEARS
        if period == PeriodEnum.OPERATIONAL_LIFETIME
        else FIXED_COSTS_PER_YEAR_2024
    )
    try:
        return costs.get(fuel_type) / DAYS_PER_YEAR
    except KeyError:
        raise KeyError(f"Missing fixed cost data for fuel type: {fuel_type}")
