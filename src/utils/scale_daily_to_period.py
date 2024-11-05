from constants.utils import DAYS_PER_YEAR, PeriodEnum
from params import OPERATIONAL_LIFETIME


def scale_daily_to_period(daily_val: float, period: PeriodEnum) -> float:
    """Scales a per-day value to the given period

    Args:
        daily_val (float): the value over one day, e.g. emissions per day, opex per day
        period (PeriodEnum): the period of time over which we want to scale the value

    Returns:
        float: the scaled value, e.g. emissions per week, opex per year
    """
    # This might become more complex in future, taking into account macroeconomic effects & inflation
    if period == PeriodEnum.DAILY:
        return daily_val
    if period == PeriodEnum.WEEKLY:
        return daily_val * 7
    if period == PeriodEnum.YEARLY:
        return daily_val * DAYS_PER_YEAR
    if period == PeriodEnum.OPERATIONAL_LIFETIME:
        return daily_val * DAYS_PER_YEAR * OPERATIONAL_LIFETIME
