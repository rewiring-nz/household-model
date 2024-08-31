from params import OPERATIONAL_LIFETIME
from openapi_client.models import Household
from savings.emissions.get_emissions_per_day import (
    get_emissions_per_day,
)
from constants.utils import PeriodEnum
from constants.machines.space_heating import SPACE_HEATING_STATS


def get_space_heating_emissions(
    household: Household,
    period: PeriodEnum = PeriodEnum.DAILY,
) -> float:
    """Calculates the emissions from space heater(s) in given household

    Args:
    household (Household): object describing a household's energy behaviour
        period (PeriodEnum, optional): the period over which to calculate the emissions. Calculations over a longer period of time (e.g. 15 years) should use this feature, as there may be external economic factors which impact the result, making it different to simply multiplying the daily emissions value. Defaults to PeriodEnum.DAILY.

    Returns:
        float: kgCO2e emitted from space heating over given period
    """
    em_daily = get_emissions_per_day(
        household.space_heating,
        SPACE_HEATING_STATS,
    )
    if period == PeriodEnum.DAILY:
        return em_daily
    if period == PeriodEnum.WEEKLY:
        return em_daily * 7
    if period == PeriodEnum.YEARLY:
        return em_daily * 365.25
    if period == PeriodEnum.OPERATIONAL_LIFETIME:
        return em_daily * 365.25 * OPERATIONAL_LIFETIME
