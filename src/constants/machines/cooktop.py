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

# ======= OLD =========

# Cooktops kWh/day
# From 'Machines'!D192
COOKTOP_COLS = [
    "Cooktop_Gas cooktop",
    "Cooktop_LPG cooktop",
    "Cooktop_Electric resistance cooktop",
    "Cooktop_Electric induction cooktop",
    "Cooktop_Don't know",
]

COOKTOP_KWH_PER_DAY = {
    "Cooktop_Gas cooktop": 2.08,
    "Cooktop_LPG cooktop": 2.08,
    "Cooktop_Electric resistance cooktop": 0.89,
    "Cooktop_Electric induction cooktop": 0.81,
}

COOKTOP_ELECTRIC_TYPES = [
    "Cooktop_Electric resistance cooktop",
    "Cooktop_Electric induction cooktop",
]

COOKTOP_TYPE_TO_FUEL_TYPE = {
    "Cooktop_Gas cooktop": "natural_gas",
    "Cooktop_LPG cooktop": "lpg",
    "Cooktop_Electric resistance cooktop": "electricity",
    "Cooktop_Electric induction cooktop": "electricity",
}

# From 'Machines'!D196
# Do NOT including fixed cost proportion, this is calculated separately
COOKTOP_OPEX_15_YRS = {
    "Cooktop_Gas cooktop": 1426.9,
    "Cooktop_LPG cooktop": 3166.6,
    "Cooktop_Electric resistance cooktop": 1402.7,
    "Cooktop_Electric induction cooktop": 1270,
}

# From 'Product prices'!D25:D27
COOKTOP_UPFRONT_COST = {
    "Cooktop_Gas cooktop": {
        "item_price": 1022,
        "install_cost": 630,
    },
    "Cooktop_LPG cooktop": {
        "item_price": 1022,
        "install_cost": 630,
    },
    "Cooktop_Electric resistance cooktop": {
        "item_price": 879,
        "install_cost": 288,
    },
    "Cooktop_Electric induction cooktop": {
        "item_price": 1430,
        "install_cost": 1265,
    },
}
