from aenum import Enum

# TODO: use these everywhere in place of magic numbers
DAYS_PER_YEAR = 365.25  # N.B. Josh's model uses 365 in some cases, like when calculating energy generated from solar, Home!C33
HOURS_PER_YEAR = 24 * DAYS_PER_YEAR  # 8766


class PeriodEnum(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    YEARLY = "YEARLY"
    OPERATIONAL_LIFETIME = "OPERATIONAL_LIFETIME"
