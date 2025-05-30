from openapi_client.models import CooktopEnum
from constants.fuel_stats import FuelTypeEnum
from constants.machines.machine_info import MachineInfoMap

# kwh_per_day are from values in Machines!D196:G196
COOKTOP_INFO: MachineInfoMap = {
    CooktopEnum.GAS: {
        "kwh_per_day": 1.94,
        "fuel_type": FuelTypeEnum.NATURAL_GAS,
    },
    CooktopEnum.LPG: {
        "kwh_per_day": 1.94,
        "fuel_type": FuelTypeEnum.LPG,
    },
    CooktopEnum.ELECTRIC_RESISTANCE: {
        "kwh_per_day": 0.83,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
    CooktopEnum.ELECTRIC_INDUCTION: {
        "kwh_per_day": 0.75,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
}

# From 'Product prices'!D25:D27
COOKTOP_UPFRONT_COST = {
    CooktopEnum.GAS: {
        "item_price": 1022,
        "install_cost": 630,
    },
    CooktopEnum.LPG: {
        "item_price": 1022,
        "install_cost": 630,
    },
    CooktopEnum.ELECTRIC_RESISTANCE: {
        "item_price": 879,
        "install_cost": 288,
    },
    CooktopEnum.ELECTRIC_INDUCTION: {
        "item_price": 1430,
        "install_cost": 1265,
    },
}
