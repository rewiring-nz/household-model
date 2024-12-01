from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.electrify_household import electrify_household
from openapi_client.models import (
    Household,
    Savings,
)
from savings.emissions.calculate_emissions import calculate_emissions
from savings.opex.calculate_opex import calculate_opex
from savings.upfront_cost.calculate_upfront_cost import calculate_upfront_cost
from models.recommend_next_action import recommend_next_action
from utils.clean_household import clean_household
from utils.validate_household import validate_household

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
def calculate_household_savings(current_household: Household) -> Savings:

    validate_household(current_household)
    current_household = clean_household(current_household)
    electrified_household = electrify_household(current_household)

    emissions = calculate_emissions(current_household, electrified_household)
    opex = calculate_opex(current_household, electrified_household)
    upfront_cost = calculate_upfront_cost(current_household, electrified_household)
    recommendation = recommend_next_action(current_household)

    savings = Savings(
        emissions=emissions,
        opex=opex,
        upfrontCost=upfront_cost,
        recommendation=recommendation,
    )
    return savings
