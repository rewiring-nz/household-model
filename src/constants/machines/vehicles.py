from constants.fuel_stats import FuelTypeEnum
from constants.machines.machine_info import MachineInfoMap
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum


# Vehicles kWh/day per vehicle
VEHICLE_INFO: MachineInfoMap = {
    VehicleFuelTypeEnum.PETROL: {
        "kwh_per_day": 31.4,
        "fuel_type": FuelTypeEnum.PETROL,
    },
    VehicleFuelTypeEnum.DIESEL: {
        "kwh_per_day": 22.8,
        "fuel_type": FuelTypeEnum.DIESEL,
    },
    VehicleFuelTypeEnum.HYBRID: [
        # Assume 70% petrol, 30% electric
        {
            "kwh_per_day": 31.4 * 0.7,
            "fuel_type": FuelTypeEnum.PETROL,
        },
        {
            "kwh_per_day": 7.324 * 0.3,
            "fuel_type": FuelTypeEnum.ELECTRICITY,
        },
    ],
    VehicleFuelTypeEnum.PLUG_IN_HYBRID: [
        # Assume 60% petrol, 40% electric
        {
            "kwh_per_day": 31.4 * 0.6,
            "fuel_type": FuelTypeEnum.PETROL,
        },
        {
            "kwh_per_day": 7.324 * 0.4,
            "fuel_type": FuelTypeEnum.ELECTRICITY,
        },
    ],
    VehicleFuelTypeEnum.ELECTRIC: {
        "kwh_per_day": 7.324,
        "fuel_type": FuelTypeEnum.ELECTRICITY,
    },
}

VEHICLE_AVG_KMS_PER_WEEK = 210

# Road User Charges (RUCs) in $/yr/1000km https://www.whattheruc.com/
RUCS = {
    VehicleFuelTypeEnum.ELECTRIC: 76,
    VehicleFuelTypeEnum.PLUG_IN_HYBRID: 38,
    VehicleFuelTypeEnum.HYBRID: 0,
    VehicleFuelTypeEnum.PETROL: 0,
    VehicleFuelTypeEnum.DIESEL: 76,
}
