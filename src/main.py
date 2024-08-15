from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openapi_client.models import (
    Household,
    Savings,
    Emissions,
    EmissionsValues,
    Opex,
    OpexValues,
)

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
def calculate_household_savings(household=Household) -> Savings:
    savings = Savings(
        emissions=Emissions(
            perWeek=EmissionsValues(
                before=500.5,
                after=100.1,
                difference=400.4
            ),
            perYear=EmissionsValues(
                before=500.5*52,
                after=100.1*52,
                difference=400.4*52
            ),
            overLifetime=EmissionsValues(
                before=500.5*52*15*1.1, # some random factor
                after=100.1*52*15*1.1,
                difference=400.4*52*15*1.1
            ),
            operationalLifetime=15
        ),
        opex=Opex(
            perWeek=OpexValues(
                before=300.52,
                after=140.11,
                difference=160.41
            ),
            perYear=OpexValues(
                before=300.52*52,
                after=140.11*52,
                difference=160.41*52
            ),
            overLifetime=OpexValues(
                before=300.52*52*15*1.1, # some random factor
                after=140.11*52*15*1.1,
                difference=160.41*52*15*1.1
            ),
            operationalLifetime=15
        ),
        upfrontCost=12345.67
    )
    return savings
