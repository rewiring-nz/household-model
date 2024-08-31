import random
from openapi_client.models import Household, Recommendation, RecommendationActionEnum

NEXT_STEP_URLS = {
    RecommendationActionEnum.SPACE_HEATING: "https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
    RecommendationActionEnum.WATER_HEATING: "https://www.rewiring.nz/electrification-guides/water-heating",
    RecommendationActionEnum.COOKING: "https://www.rewiring.nz/electrification-guides/cooktops",
    RecommendationActionEnum.VEHICLE: "https://www.rewiring.nz/electrification-guides/electric-cars",
    RecommendationActionEnum.SOLAR: "https://www.rewiring.nz/electrification-guides/solar",
    RecommendationActionEnum.BATTERY: "https://www.rewiring.nz/electrification-guides/home-batteries",
}


def recommend_next_action(household: Household) -> Recommendation:
    # TODO: actually implement the algorithm, this is just a dummy filler
    next_action = random.choice(list(RecommendationActionEnum))
    return Recommendation(
        action=next_action,
        url=NEXT_STEP_URLS.get(next_action),
    )
