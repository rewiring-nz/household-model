from typing import List
from models.electrify_household import (
    electrify_cooktop,
    electrify_space_heating,
    electrify_vehicle,
    electrify_water_heating,
    should_electrify,
    should_install,
)
from openapi_client.models import Household, Recommendation, RecommendationActionEnum
from openapi_client.models.vehicle import Vehicle
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum

NEXT_STEP_URLS = {
    RecommendationActionEnum.SPACE_HEATING: "https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
    RecommendationActionEnum.WATER_HEATING: "https://www.rewiring.nz/electrification-guides/water-heating",
    RecommendationActionEnum.COOKING: "https://www.rewiring.nz/electrification-guides/cooktops",
    RecommendationActionEnum.VEHICLE: "https://www.rewiring.nz/electrification-guides/electric-cars",
    RecommendationActionEnum.SOLAR: "https://www.rewiring.nz/electrification-guides/solar",
    RecommendationActionEnum.BATTERY: "https://www.rewiring.nz/electrification-guides/home-batteries",
    RecommendationActionEnum.FULLY_ELECTRIFIED: None,
}


def recommend_next_action(household: Household) -> Recommendation:
    """Heuristic algorithm to recommend the next step action based on household inputs

    Args:
        household (Household): household inputs

    Returns:
        Recommendation: the next step that the user should take for electrification
    """
    action = RecommendationActionEnum.FULLY_ELECTRIFIED

    # In priority order:

    # 1. Rooftop solar
    if should_install(household.solar):
        action = RecommendationActionEnum.SOLAR

    # 2. First EV
    elif (
        n_vehicles_to_electrify(household.vehicles) > 0
        and n_evs(household.vehicles) == 0
    ):
        action = RecommendationActionEnum.VEHICLE

    # 3. Space heater
    elif should_electrify(household.space_heating, electrify_space_heating):
        action = RecommendationActionEnum.SPACE_HEATING

    # 4. Water heater
    elif should_electrify(household.water_heating, electrify_water_heating):
        action = RecommendationActionEnum.WATER_HEATING

    # 5. Cooktop
    elif should_electrify(household.cooktop, electrify_cooktop):
        action = RecommendationActionEnum.COOKING

    # 6. Battery
    elif should_install(household.battery):
        action = RecommendationActionEnum.BATTERY

    # 7. All other vehicles
    elif n_vehicles_to_electrify(household.vehicles) > 0:
        action = RecommendationActionEnum.VEHICLE

    return Recommendation(action=action, url=NEXT_STEP_URLS.get(action))


def n_evs(vehicles: List[Vehicle]) -> int:
    """Calculates the number of EVs vehicles in the list

    Args:
        vehicles (List[Vehicle]): list of vehicles and their fuel type info

    Returns:
        int: the number of EVs in the list
    """
    return sum([v.fuel_type == VehicleFuelTypeEnum.ELECTRIC for v in vehicles])


def n_vehicles_to_electrify(vehicles: List[Vehicle]) -> int:
    """Calculates the number of vehicles in the list to electrify

    Args:
        vehicles (List[Vehicle]): list of vehicles and their fuel type info

    Returns:
        int: the number of vehicles still to electrify
    """
    return sum([should_electrify(v, electrify_vehicle) for v in vehicles])
