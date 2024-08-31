import pandas as pd
from typing import List, TypedDict
from constants.fuel_stats import COST_PER_FUEL_KWH_TODAY, FuelTypeEnum
from constants.machines.machine_info import MachineInfoMap
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum


# Vehicles kWh/day per vehicle
# From 'Machines'!D273
# TODO: Update with latest numbers https://docs.google.com/spreadsheets/d/1_eAAx5shTHSJAUuHdfj7AQafS0BZJn_0F48yngCpFXI/edit?disco=AAABVW3cP-k
VEHICLE_INFO: MachineInfoMap = {
    VehicleFuelTypeEnum.PETROL: {
        "kwh_per_day": 32,
        "fuel_type": FuelTypeEnum.PETROL,
    },
    VehicleFuelTypeEnum.DIESEL: {
        "kwh_per_day": 28.4,
        "fuel_type": FuelTypeEnum.DIESEL,
    },
    # For PHEV and HEV, we're going to assume the emissions are a % of a petrol car, and the rest is electric
    VehicleFuelTypeEnum.HYBRID: {
        "kwh_per_day": None,
        "fuel_type": None,
    },
    VehicleFuelTypeEnum.PLUG_IN_HYBRID: {
        "kwh_per_day": None,
        "fuel_type": None,
    },
    VehicleFuelTypeEnum.ELECTRIC: {
        "kwh_per_day": 8.027,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
}

# TODO: Get the value per vehicle, not per capita (because 1 vehicle could be shared by multiple people)
VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA = 11000


# in $/yr/1000km https://www.whattheruc.com/
RUCS = {
    "Electric": 76,
    "Plug-in Hybrid": 38,
    "Hybrid": 0,
    "Petrol": 0,
    "Diesel": 76,
}

# ======= OLD =========

VEHICLE_FUEL_TYPE_COLS = [
    "Vehicles fuel/energy type_Vehicle 1",
    "Vehicles fuel/energy type_Vehicle 2",
    "Vehicles fuel/energy type_Vehicle 3",
    "Vehicles fuel/energy type_Vehicle 4",
    "Vehicles fuel/energy type_Vehicle 5",
]


VEHICLE_DISTANCE_COLS = [
    "Vehicles distance_Vehicle 1",
    "Vehicles distance_Vehicle 2",
    "Vehicles distance_Vehicle 3",
    "Vehicles distance_Vehicle 4",
    "Vehicles distance_Vehicle 5",
]

VEHICLE_WEEKLY_DISTANCE_MAP = {
    "0-50km": 25,
    "50-99km": 75,
    "100-199km": 150,
    "200+ km": 250,
}


class VehicleStats(TypedDict):
    fuel_type: str
    distance_per_yr: str


def extract_vehicle_stats(household: pd.Series) -> List[VehicleStats]:
    # TODO: The processing of these distance string columns into numbers should be done during the processing step
    # Otherwise what's input here is half-processed, where the "Vehicles" column has already been cast to an int,
    # but the distance cols are still strings of ranges

    stats = []
    num_vehicles = household["Vehicles"]
    if num_vehicles == 0:
        return stats

    # Ignore vehicles past 5; we don't have fuel type & distance data for them
    if num_vehicles > 5:
        num_vehicles = 5

    for i in range(num_vehicles):

        fuel_type = household[f"Vehicles fuel/energy type_Vehicle {i+1}"]
        if fuel_type == "I’m not sure":
            continue

        distance_per_wk_range = household[f"Vehicles distance_Vehicle {i+1}"]
        if distance_per_wk_range == "I’m not sure":
            distance_per_yr = VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA
        else:
            distance_per_yr = VEHICLE_WEEKLY_DISTANCE_MAP[distance_per_wk_range] * 52

        stats.append(
            {
                "fuel_type": fuel_type,
                "distance_per_yr": distance_per_yr,
            }
        )
    return stats


VEHICLE_ELECTRIC_TYPES = [
    "Electric",
    # "Plug-in Hybrid",
]

# kgCO2e
# from Electric Homes report which uses https://www.transportenvironment.org/articles/how-clean-are-electric-cars/
VEHICLE_EMBODIED_EMISSIONS = {
    "Electric": 1000
    * (12.3 + 9.9)
    / 2,  # 11.1, halfway between 12.3T for chinese EVs, and 9.9T for Swedish EVs
    "Petrol": 1000 * 6.7,
    "Diesel": 1000 * 7.0,
}

VEHICLE_TYPE_TO_FUEL_TYPE = {
    "Electric": "electricity",
    # "Plug-in Hybrid": "electricity",
    # "Hybrid": "petrol",
    "Petrol": "petrol",
    "Diesel": "diesel",
}


# From 'Machines'!D280
# TODO: Make this dynamic to operating lifetime (years)
VEHICLE_OPEX_15_YRS = {
    "Electric": 10646,
    # "Plug-in Hybrid": 0,
    # "Hybrid": 0,
    "Petrol": 48038,
    "Diesel": 32106,
}
