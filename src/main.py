from fastapi import FastAPI
from openapi_client.models import (
    Household,
    Savings,
    Emissions,
    EmissionsValues,
    Opex,
    OpexValues,
)

app = FastAPI()


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
