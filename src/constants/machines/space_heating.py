from openapi_client.models import SpaceHeatingEnum
from constants.fuel_stats import FuelTypeEnum
from constants.machines.machine_info import MachineInfoMap
from openapi_client.models.location_enum import LocationEnum

# kwh_per_day are from values in Machines!D75:J75, which are average for the whole house
# https://docs.google.com/spreadsheets/d/1_eAAx5shTHSJAUuHdfj7AQafS0BZJn_0F48yngCpFXI/edit?gid=0#gid=0

SPACE_HEATING_INFO: MachineInfoMap = {
    SpaceHeatingEnum.WOOD: {
        "kwh_per_day": 14.44,
        "fuel_type": FuelTypeEnum.WOOD,
    },
    SpaceHeatingEnum.GAS: {
        "kwh_per_day": 11.73,
        "fuel_type": FuelTypeEnum.NATURAL_GAS,
    },
    SpaceHeatingEnum.LPG: {
        "kwh_per_day": 11.73,
        "fuel_type": FuelTypeEnum.LPG,
    },
    SpaceHeatingEnum.ELECTRIC_RESISTANCE: {
        "kwh_per_day": 9.39,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
    SpaceHeatingEnum.ELECTRIC_HEAT_PUMP: {
        "kwh_per_day": 2.3,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
    SpaceHeatingEnum.DONT_KNOW: {
        "kwh_per_day": None,
        "fuel_type": None,
    },
}

# From 'Product prices'!E8
SPACE_HEATING_UPFRONT_COST = {
    SpaceHeatingEnum.ELECTRIC_HEAT_PUMP: {
        "item_price": 2728,
        "install_cost": 1050,
    },
    # Everything else below here is kind of irrelevant, since we'll only ever be recommending heat pumps
    SpaceHeatingEnum.GAS: {
        "item_price": (3825 + 3927.17) / 2,  # D78, D82
        "install_cost": 1250,
    },
    SpaceHeatingEnum.LPG: {
        "item_price": (3825 + 3927.17) / 2,  # D90,D93
        "install_cost": 1250,
    },
    SpaceHeatingEnum.WOOD: {
        "item_price": 4913,
        "install_cost": 0,
    },
    SpaceHeatingEnum.ELECTRIC_RESISTANCE: {
        "item_price": 300,  # TODO: Should check this again, although we'd never recommend it over heat pumps
        "install_cost": 0,
    },
}

N_HEAT_PUMPS_NEEDED_PER_LOCATION = {
    LocationEnum.NORTHLAND: 1,
    LocationEnum.AUCKLAND_NORTH: 1,
    LocationEnum.AUCKLAND_CENTRAL: 1,
    LocationEnum.AUCKLAND_EAST: 1,
    LocationEnum.AUCKLAND_WEST: 1,
    LocationEnum.AUCKLAND_SOUTH: 1,
    LocationEnum.WAIKATO: 1,
    LocationEnum.BAY_OF_PLENTY: 1,
    LocationEnum.GISBORNE: 1,
    LocationEnum.HAWKES_BAY: 1,
    LocationEnum.TARANAKI: 2,
    LocationEnum.MANAWATU_WANGANUI: 2,
    LocationEnum.WELLINGTON: 3,
    LocationEnum.TASMAN: 2,
    LocationEnum.NELSON: 2,
    LocationEnum.MARLBOROUGH: 2,
    LocationEnum.WEST_COAST: 3,
    LocationEnum.CANTERBURY: 2,
    LocationEnum.OTAGO: 3,
    LocationEnum.SOUTHLAND: 3,
    LocationEnum.STEWART_ISLAND: 3,
    LocationEnum.CHATHAM_ISLANDS: 3,
    LocationEnum.GREAT_BARRIER_ISLAND: 2,
    LocationEnum.OVERSEAS: 2,
    LocationEnum.OTHER: 2,
}


# ======= OLD =========

# These are multi-choice boolean (yes/no) columns. Households may have more than one type.
SPACE_HEATING_BOOL_COLS = [
    "Home heating_Heat pump split system (an individual unit in a room(s))",
    "Home heating_Heat pump central system (one indoor unit for the entire home)",
    "Home heating_Gas small heater(s) (not LPG)",
    "Home heating_LPG small heater(s)",
    "Home heating_Gas fireplac(s) (not LPG)",
    "Home heating_LPG fireplace(s)",
    "Home heating_Wood fireplace(s)",
    "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)",
    "Home heating_Central diesel heating",
    "Home heating_Underfloor diesel heating",
    "Home heating_Underfloor electric heating",
    "Home heating_Coal heating",
    # "Home heating_None",  # to be ignored in calculation
]

# These are number cols, but they are strings. Need to be converted to int.
SPACE_HEATING_NUM_COLS = [
    "Home heating number_Heat pump split system (an individual unit in a room(s))",
    "Home heating number_Gas or LPG small heater",
    "Home heating number_Gas or LPG fireplace",
    "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)",
    "Home heating number_Wood fireplace",
    "Home heating number_Diesel heater",
]


# Home heating kWh/day
# From 'Machines'!D71

# The boolean columns which represent a central system (quantity defaults to 1)
CENTRAL_SYSTEMS = [
    "Home heating_Heat pump central system (one indoor unit for the entire home)",
    "Home heating_Central diesel heating",
    "Home heating_Underfloor diesel heating",
    "Home heating_Underfloor electric heating",
    # Excluding coal for now, as it is a minority that skews results.
    # "Home heating_Coal heating",  # Doesn't have a number column equivalent. Probably a firepit. Assume quantity 1.
]

# The boolean columns which have num_column equivalents to indicate quantity
INDIVIDUAL_SYSTEMS = {
    "Home heating_Heat pump split system (an individual unit in a room(s))": "Home heating number_Heat pump split system (an individual unit in a room(s))",
    "Home heating_Gas small heater(s) (not LPG)": "Home heating number_Gas or LPG small heater",
    "Home heating_LPG small heater(s)": "Home heating number_Gas or LPG small heater",
    "Home heating_Gas fireplac(s) (not LPG)": "Home heating number_Gas or LPG fireplace",
    "Home heating_LPG fireplace(s)": "Home heating number_Gas or LPG fireplace",
    "Home heating_Wood fireplace(s)": "Home heating number_Wood fireplace",
    "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)",
    "Home heating_Diesel heater (MISSING FROM SURVEY)": "Home heating number_Diesel heater",
}


# Using the values in Machines!D71:J71 which are average for the whole house
# then dividing by reasonable-ish ratios based on the SPACE_HEATING_REPLACEMENT_RATIOS
SPACE_HEATING_KWH_PER_DAY = {
    # Boolean columns (1 or 0)
    "Home heating_Heat pump split system (an individual unit in a room(s))": 2.7 / 2,
    "Home heating_Heat pump central system (one indoor unit for the entire home)": 2.7,
    "Home heating_Gas small heater(s) (not LPG)": 11.6 / 4,
    "Home heating_LPG small heater(s)": 11.6 / 4,
    "Home heating_Gas fireplac(s) (not LPG)": 11.6 / 2,
    "Home heating_LPG fireplace(s)": 11.6 / 2,
    "Home heating_Wood fireplace(s)": 14.3,
    "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 9.3
    / 4,
    "Home heating_Central diesel heating": 12.8,  # COP of 73% from 'Misc'!B19
    "Home heating_Underfloor diesel heating": 12.8,  # COP of 73% from 'Misc'!B19
    "Home heating_Underfloor electric heating": 9.3,
    # COP of 10%, page 6 of https://environment.govt.nz/assets/Publications/Files/warm-homes-heating-options-phase1.pdf
    "Home heating_Coal heating": 9.32 * (1 / 0.1),
    # "Home heating_None" # to be ignored in calculation
    # Num columns (1 to 5 or None)
    "Home heating number_Heat pump split system (an individual unit in a room(s))": 2.7
    / 2,
    "Home heating number_Gas or LPG small heater": 11.6 / 4,
    "Home heating number_Gas or LPG fireplace": 11.6 / 2,
    "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 9.3
    / 8,
    "Home heating number_Wood fireplace": 14.3,
    "Home heating number_Diesel heater": 12.8 / 4,
    # Other (free text)
    "pellet": 9.32 * (1 / 0.835),  # COP of 83.5% from 'Misc'!B18
}

SPACE_HEATING_TYPE_TO_FUEL_TYPE = {
    # Boolean columns
    "Home heating_Heat pump split system (an individual unit in a room(s))": "electricity",
    "Home heating_Heat pump central system (one indoor unit for the entire home)": "electricity",
    "Home heating_Gas small heater(s) (not LPG)": "natural_gas",
    "Home heating_LPG small heater(s)": "lpg",
    "Home heating_Gas fireplac(s) (not LPG)": "natural_gas",
    "Home heating_LPG fireplace(s)": "lpg",
    "Home heating_Wood fireplace(s)": "wood",
    "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": "electricity",
    "Home heating_Central diesel heating": "diesel",
    "Home heating_Underfloor diesel heating": "diesel",
    "Home heating_Underfloor electric heating": "electricity",
    # "Home heating_Coal heating": 'coal', # exclude from analysis
    # "Home heating_None": None,  # exclude from analysis
    # Num columns
    "Home heating number_Heat pump split system (an individual unit in a room(s))": "electricity",
    # For the next two since gas & LPG have basically the same emissions factor, going to just use one (the lower one, for a conservative estimate)
    "Home heating number_Gas or LPG small heater": "natural_gas",
    "Home heating number_Gas or LPG fireplace": "natural_gas",
    "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": "electricity",
    "Home heating number_Wood fireplace": "wood",
    "Home heating number_Diesel heater": "diesel",
}

SPACE_HEATING_ELECTRIC_TYPES = [
    k for k, v in SPACE_HEATING_TYPE_TO_FUEL_TYPE.items() if v == "electricity"
]


# TODO: Turn these into nested dicts with fields per heater type like "opex_15_yrs", "upfront_cost", "power_output"

# From 'Machines'!M76
# Energy bills over lifetime (15yr)
# excluding fixed costs for things like gas, which are calculated separately in get_fixed_costs_per_year()
SPACE_HEATING_OPEX_15_YRS = {
    # Boolean columns (1 or 0)
    "Home heating_Heat pump split system (an individual unit in a room(s))": 4194,  # Q76
    "Home heating_Heat pump central system (one indoor unit for the entire home)": 4194,  # Q76
    "Home heating_Gas small heater(s) (not LPG)": 7981,
    "Home heating_LPG small heater(s)": 17713,
    "Home heating_Gas fireplac(s) (not LPG)": 7981,
    "Home heating_LPG fireplace(s)": 17713,
    "Home heating_Wood fireplace(s)": 8883,
    "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 14680,
    "Home heating_Central diesel heating": 14590,
    "Home heating_Underfloor diesel heating": 14590,
    "Home heating_Underfloor electric heating": 14680,
    # "Home heating_Coal heating": 1500,  # Assuming slightly higher than wood # EXCLUDED
    # "Home heating_None" # to be ignored in calculation
    # Num columns (1 to 5 or None)
    "Home heating number_Heat pump split system (an individual unit in a room(s))": 4194,  # Q76
    "Home heating number_Gas or LPG small heater": 7981
    + 4885,  # N76 + N77 (conservative estimate with lower nat gas price)
    "Home heating number_Gas or LPG fireplace": 7981,
    "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 14680,
    "Home heating number_Wood fireplace": 8883,
    "Home heating number_Diesel heater": 14590,
    # Other (free text)
    "pellet": 10000,  # Assuming slightly higher than wood burner TODO: get sources
}

# Assumes switching to individual heat pumps
# medium heat pumps nededed per heating type
SPACE_HEATING_REPLACEMENT_RATIOS = {
    "Home heating_Gas small heater(s) (not LPG)": 0.5,
    "Home heating_LPG small heater(s)": 0.5,
    "Home heating_Gas fireplac(s) (not LPG)": 1,
    "Home heating_LPG fireplace(s)": 1,
    "Home heating_Wood fireplace(s)": 2,
    "Home heating_Central diesel heating": 2,
    "Home heating_Underfloor diesel heating": 2,
    "Home heating_Coal heating": 2,
    "Home heating number_Gas or LPG small heater": 0.5,
    "Home heating number_Gas or LPG fireplace": 1,
    "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 0.25,
    "Home heating number_Wood fireplace": 2,
    "Home heating number_Diesel heater": 0.5,
}
