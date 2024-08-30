from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openapi_client.models import (
    Household,
    Savings,
    Recommendation,
    RecommendationActionEnum,
)
from savings.emissions_savings import calculate_emissions
from savings.opex_savings import calculate_opex
from savings.upfront_cost import calculate_upfront_cost

app = FastAPI()

origins = [
    "*"
    # TODO: Lock this down to just the deployed frontend app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/savings")
def calculate_household_savings(household: Household) -> Savings:
    emissions = calculate_emissions(household)
    opex = calculate_opex(household)
    upfront_cost = calculate_upfront_cost(household)

    savings = Savings(
        emissions=emissions,
        opex=opex,
        upfrontCost=upfront_cost,
        recommendation=Recommendation(
            action=RecommendationActionEnum("SPACE_HEATING"),
            url="https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
        ),
    )
    return savings
