from constants.fuel_stats import EMISSIONS_FACTORS
from constants.machines.appliance import ApplianceEnum, ApplianceInfo
from constants.machines.other_machines import ENERGY_NEEDS_OTHER_MACHINES_PER_DAY
from params import OPERATIONAL_LIFETIME
from savings.emissions.get_emissions_per_day import (
    get_emissions_per_day,
)
from constants.utils import PeriodEnum


def get_appliance_emissions(
    appliance: ApplianceEnum,
    appliance_info: ApplianceInfo,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the emissions from appliance in given household

    Args:
        appliance (ApplianceEnum): the appliance
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from appliance over given period
    """
    emissions_daily = get_emissions_per_day(
        appliance,
        appliance_info,
    )
    return _convert_to_period(emissions_daily, period)


def get_other_appliance_emissions(period: PeriodEnum = PeriodEnum.DAILY) -> float:
    """Calculates the emissions of other appliances in a household
    These may include space cooling (fans, aircon), refrigeration, laundry, lighting, etc.
    We assume that these are all electric.

    Args:
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from other appliances over given period
    """
    emissions_daily = (
        ENERGY_NEEDS_OTHER_MACHINES_PER_DAY * EMISSIONS_FACTORS["electricity"]
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
