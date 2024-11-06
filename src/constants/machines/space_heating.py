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
        # Need to update, but low priority because we'd never recommend it over heat pumps
        "item_price": 300,
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
