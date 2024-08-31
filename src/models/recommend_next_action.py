from openapi_client.models import Household, Recommendation, RecommendationActionEnum


def recommend_next_action(household: Household) -> Recommendation:
    return Recommendation(
        action=RecommendationActionEnum("SPACE_HEATING"),
        url="https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
    )
