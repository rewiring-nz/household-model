from constants.fuel_stats import FuelTypeEnum
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

# Road User Charges (RUCs) in $/yr/1000km https://www.whattheruc.com/
RUCS = {
    VehicleFuelTypeEnum.ELECTRIC: 76,
    VehicleFuelTypeEnum.PLUG_IN_HYBRID: 38,
    VehicleFuelTypeEnum.HYBRID: 0,
    VehicleFuelTypeEnum.PETROL: 0,
    VehicleFuelTypeEnum.DIESEL: 76,
}
