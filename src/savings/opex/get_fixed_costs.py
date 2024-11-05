from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.household import Household
from openapi_client.models.space_heating_enum import SpaceHeatingEnum

from constants.fuel_stats import FuelTypeEnum
from constants.utils import PeriodEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from savings.opex.get_machine_opex import FIXED_COSTS_PER_YEAR
from utils.scale_daily_to_period import scale_daily_to_period


def get_fixed_costs(
    household: Household,
    period: PeriodEnum = PeriodEnum.DAILY,
    ignore_lpg_if_ngas_present: bool = False,
) -> float:
    """Calculates the fixed costs you pay per year, for gas and LPG connections.
    Always includes electricity fixed costs, since all households pay this anyway
    for all the other devices we have (we assume the house stays on the grid).

    Args:
        household (Household): TODO
        period (PeriodEnum, optional): _description_. Defaults to PeriodEnum.DAILY.

    Returns:
        float: _description_
    """
    # TODO: unit test, use tests for get_fixed_costs_per_year()
    # These values are all in daily
    grid_connection = FIXED_COSTS_PER_YEAR.get(FuelTypeEnum.ELECTRICITY) / 365.25
    ngas_connection = 0
    lpg_connection = 0
    if (
        household.space_heating == SpaceHeatingEnum.GAS
        or household.water_heating == WaterHeatingEnum.GAS
        or household.cooktop == CooktopEnum.GAS
    ):
        ngas_connection = FIXED_COSTS_PER_YEAR.get(FuelTypeEnum.NATURAL_GAS) / 365.25
    if (
        household.space_heating == SpaceHeatingEnum.LPG
        or household.water_heating == WaterHeatingEnum.LPG
        or household.cooktop == CooktopEnum.LPG
    ):
        lpg_connection = FIXED_COSTS_PER_YEAR.get(FuelTypeEnum.LPG) / 365.25

    if ignore_lpg_if_ngas_present and ngas_connection > 0:
        # Ignore LPG if they've also said they have ngas, because most homes are unlikely to have both an LPG and ngas connection. They are most likely referring to an outdoor BBQ as their "LPG cooktop" or something similar that's uncommonly used and not their usual mode of energy use.
        lpg_connection = 0

    fixed_costs_daily = grid_connection + ngas_connection + lpg_connection
    return scale_daily_to_period(fixed_costs_daily, period)
