from typing import Dict, Optional, TypedDict
from constants.fuel_stats import FuelTypeEnum
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum

MachineEnum = SpaceHeatingEnum | WaterHeatingEnum | CooktopEnum | VehicleFuelTypeEnum


class MachineInfo(TypedDict):
    kwh_per_day: Optional[float]  # kWh/day
    fuel_type: Optional[FuelTypeEnum]  # kgCO2e/kWh


MachineInfoMap = Dict[MachineEnum, MachineInfo]
