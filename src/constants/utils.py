from aenum import Enum


class PeriodEnum(str, Enum):
    DAILY = "DAILY"
    YEARLY = "YEARLY"
    OPERATIONAL_LIFETIME = "OPERATIONAL_LIFETIME"
