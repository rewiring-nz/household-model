from openapi_client.models import CooktopEnum
from constants.fuel_stats import FuelTypeEnum
from constants.machines.machine_info import MachineInfoMap

# kwh_per_day are from values in Machines!D196:G196
# https://docs.google.com/spreadsheets/d/1_eAAx5shTHSJAUuHdfj7AQafS0BZJn_0F48yngCpFXI/edit?gid=0#gid=0

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
    # CooktopEnum.WOOD: {
    #     "kwh_per_day": 14.44, # Need a value for this
    #     "fuel_type": FuelTypeEnum.WOOD,
    # },
    CooktopEnum.DONT_KNOW: {
        "kwh_per_day": None,
        "fuel_type": None,
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
    # CooktopEnum.WOOD: {
    #     "item_price": 0,
    #     "install_cost": 0,
    # },
    CooktopEnum.DONT_KNOW: {
        "item_price": 0,
        "install_cost": 0,
    },
}
