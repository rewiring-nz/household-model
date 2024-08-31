from typing import Dict, Optional, TypedDict
from constants.fuel_stats import FuelTypeEnum
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum

ApplianceEnum = SpaceHeatingEnum | WaterHeatingEnum | CooktopEnum


class ApplianceTypeInfo(TypedDict):
    kwh_per_day: Optional[float]  # kWh/day
    fuel_type: Optional[FuelTypeEnum]  # kgCO2e/kWh


ApplianceInfo = Dict[ApplianceEnum, ApplianceTypeInfo]
