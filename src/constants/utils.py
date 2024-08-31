from aenum import Enum


class PeriodEnum(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    YEARLY = "YEARLY"
    OPERATIONAL_LIFETIME = "OPERATIONAL_LIFETIME"
