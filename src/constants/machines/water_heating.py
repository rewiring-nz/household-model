from openapi_client.models import WaterHeatingEnum
from constants.fuel_stats import FuelTypeEnum
from constants.machines.machine_info import MachineInfoMap

# kwh_per_day are from values in Machines!D141:J141
# https://docs.google.com/spreadsheets/d/1_eAAx5shTHSJAUuHdfj7AQafS0BZJn_0F48yngCpFXI/edit?gid=0#gid=0

WATER_HEATING_INFO: MachineInfoMap = {
    WaterHeatingEnum.GAS: {
        "kwh_per_day": 6.6,
        "fuel_type": FuelTypeEnum.NATURAL_GAS,
    },
    WaterHeatingEnum.LPG: {
        "kwh_per_day": 6.6,
        "fuel_type": FuelTypeEnum.LPG,
    },
    WaterHeatingEnum.ELECTRIC_RESISTANCE: {
        "kwh_per_day": 6.97,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
    WaterHeatingEnum.ELECTRIC_HEAT_PUMP: {
        "kwh_per_day": 1.71,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
    WaterHeatingEnum.SOLAR: {
        # This is not solar panels but pure solar, rooftop direct heating of water with sun heat e.g. Solahart
        "kwh_per_day": 1.71,  # Need to check this, but assume same as heat pump for now
        "fuel_type": FuelTypeEnum.SOLAR,
    },
    WaterHeatingEnum.DONT_KNOW: {
        "kwh_per_day": None,
        "fuel_type": None,
    },
}

# From 'Product prices'!D17:D21
WATER_HEATING_UPFRONT_COST = {
    WaterHeatingEnum.ELECTRIC_RESISTANCE: {
        "item_price": 1975,  # C18 (assuming large size since average of heat pump list is around 300L)
        "install_cost": 1995,  # D18
    },
    WaterHeatingEnum.GAS: {
        "item_price": 1418,  # C20
        "install_cost": 2175,  # D20
    },
    WaterHeatingEnum.LPG: {
        "item_price": 1419,  # C21
        "install_cost": 2175,  # D21
    },
    WaterHeatingEnum.ELECTRIC_HEAT_PUMP: {
        "item_price": 4678,  # C17
        "install_cost": 2321,  # D17
    },
    WaterHeatingEnum.SOLAR: {
        # Not sure on price but also low priority because we don't recommend switching to rooftop direct-solar water heating (like Solahart)
        "item_price": None,
        "install_cost": None,
    },
    WaterHeatingEnum.DONT_KNOW: {
        "item_price": 0,
        "install_cost": 0,
    },
}
