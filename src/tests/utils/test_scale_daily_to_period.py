from constants.utils import PeriodEnum
from utils.scale_daily_to_period import scale_daily_to_period


class TestConvertToPeriod:
    def test_it_returns_daily_emissions(self):
        result = scale_daily_to_period(1, PeriodEnum.DAILY)
        assert result == 1

    def test_it_returns_weekly_emissions(self):
        result = scale_daily_to_period(1, PeriodEnum.WEEKLY)
        assert result == 1 * 7

    def test_it_returns_yearly_emissions(self):
        result = scale_daily_to_period(1, PeriodEnum.YEARLY)
        assert result == 1 * 365.25

    def test_it_returns_operational_lifetime_emissions(self):
        result = scale_daily_to_period(1, PeriodEnum.OPERATIONAL_LIFETIME)
        assert result == 1 * 365.25 * 15
