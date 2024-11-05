from aenum import Enum

DAYS_PER_YEAR = 365.25  # N.B. Josh's model uses 365 in some cases, like when calculating energy generated from solar, Home!C33
WEEKS_PER_YEAR = 52
HOURS_PER_YEAR = 24 * DAYS_PER_YEAR  # 8766


class PeriodEnum(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    YEARLY = "YEARLY"
    OPERATIONAL_LIFETIME = "OPERATIONAL_LIFETIME"
