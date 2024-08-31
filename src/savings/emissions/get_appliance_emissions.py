from typing import Dict, Optional, TypedDict
from constants.fuel_stats import FuelTypeEnum
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from params import OPERATIONAL_LIFETIME
from openapi_client.models import Household
from savings.emissions.get_emissions_per_day import (
    get_emissions_per_day,
)
from constants.utils import PeriodEnum


ApplianceEnum = SpaceHeatingEnum | WaterHeatingEnum | CooktopEnum


class ApplianceTypeInfo(TypedDict):
    kwh_per_day: Optional[float]
    fuel_type: Optional[FuelTypeEnum]


ApplianceInfo = Dict[ApplianceEnum, ApplianceTypeInfo]


def get_appliance_emissions(
    household: Household,
    appliance_info: ApplianceInfo,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the emissions from appliance in given household

    Args:
        household (Household): object describing a household's energy behaviour
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from appliance over given period
    """
    emissions_daily = get_emissions_per_day(
        household.space_heating,
        appliance_info,
    )
    return _convert_to_period(emissions_daily, period)


def _convert_to_period(emissions_daily: float, period: PeriodEnum) -> float:
    # This might become more complex in future, taking into account macroeconomic effects
    if period == PeriodEnum.DAILY:
        return emissions_daily
    if period == PeriodEnum.WEEKLY:
        return emissions_daily * 7
    if period == PeriodEnum.YEARLY:
        return emissions_daily * 365.25
    if period == PeriodEnum.OPERATIONAL_LIFETIME:
        return emissions_daily * 365.25 * OPERATIONAL_LIFETIME
