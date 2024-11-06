from constants.machines.vehicles import VEHICLE_AVG_KMS_PER_WEEK
from openapi_client.models.household import Household
from openapi_client.models.vehicle import Vehicle


def clean_household(household: Household) -> Household:
    household.vehicles = [clean_vehicle(v) for v in household.vehicles]
    return household


def clean_vehicle(vehicle: Vehicle) -> Vehicle:
    return vehicle.copy(
        update={
            "kms_per_week": (
                round(VEHICLE_AVG_KMS_PER_WEEK)
                if vehicle.kms_per_week is None
                else vehicle.kms_per_week
            )
        }
    )
