from constants.machines.vehicles import VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA
from openapi_client.models.household import Household
from openapi_client.models.vehicle import Vehicle


def clean_household(household: Household) -> Household:
    household.vehicles = [clean_vehicle(v) for v in household.vehicles]
    return household


def clean_vehicle(vehicle: Vehicle) -> Vehicle:
    return vehicle.copy(
        update={
            "kms_per_week": (
                # average per capita is  212 km/week
                # TODO: use average per vehicle, not capita
                round(VEHICLE_AVG_DISTANCE_PER_YEAR_PER_CAPITA / 52)
                if vehicle.kms_per_week is None
                else vehicle.kms_per_week
            )
        }
    )
