from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from pydantic.types import conint
from typing import List
from enum import Enum
from client.models import Household, Savings
app = FastAPI()

ConfigDict.arbitrary_types_allowed = True  


# # TODO: turn these into actual form inputs
# class LocationEnum(str, Enum):
#     NORTHLAND = "Northland / Te Tai Tokerau"
#     GREAT_BARRIER_ISLAND = "Great Barrier Island / Aotea"
#     AUCKLAND = "Auckland / Tāmaki Makaurau"
#     WAIKATO = "Waikato"
#     BAY_OF_PLENTY = "Bay of Plenty / Te Moana-a-Toi"
#     GISBORNE = "Gisborne / Tairāwhiti"
#     HAWKES_BAY = "Hawke's Bay / Te Matau-a-Māui"
#     TARANAKI = "Taranaki"
#     MANAWATU_WANGANUI = "Manawatu-Wanganui"
#     WELLINGTON = "Wellington / Te Whanganui a Tara"
#     TASMAN = "Tasman / Te Tai o Aorere"
#     NELSON = "Nelson / Whakatū"
#     MARLBOROUGH = "Marlborough / Te Tauihu-o-te-waka"
#     WEST_COAST = "West Coast / Te Tai Poutini"
#     CANTERBURY = "Canterbury / Waitaha"
#     CHRISTCHURCH = "Christchurch / Ōtautahi"
#     OTAGO = "Otago"
#     DUNEDIN = "Dunedin / Ōtepoti"
#     SOUTHLAND = "Southland / Murihiku"
#     STEWART_ISLAND = "Stewart Island / Rakiura"
#     CHATHAM_ISLANDS = "Chatham Islands / Rēkohu / Wharekauri"
#     OVERSEAS = "Overseas"
#     OTHER = "Other"


# class SpaceHeaterEnum(str, Enum):
#     ELECTRIC_HEAT_PUMP = "Electric heat pump"
#     ELECTRIC_RESISTANCE = "Electric resistance"
#     GAS = "Gas (piped/ducted)"
#     LPG = "LPG bottles"
#     WOOD = "Wood burner"
#     DONT_KNOW = "Don't know"


# class WaterHeaterEnum(str, Enum):
#     ELECTRIC_HEAT_PUMP = "Electric heat pump"
#     ELECTRIC_RESISTANCE = "Electric resistance"
#     GAS = "Gas (piped/ducted)"
#     LPG = "LPG bottles"
#     SOLAR = "Solar water heater"
#     WOOD = "Wood burner"
#     DONT_KNOW = "Don't know"


# class CooktopEnum(str, Enum):
#     ELECTRIC_INDUCTION = "Electric induction"
#     ELECTRIC_RESISTANCE = "Electric resistance"
#     GAS = "Gas (piped/ducted)"
#     LPG = "LPG bottles"
#     WOOD = "Wood"
#     DONT_KNOW = "Don't know"


# class FuelTypeEnum(str, Enum):
#     PETROL = "Petrol"
#     DIESEL = "Diesel"
#     ELECTRIC = "Electric (BEV)"
#     PLUG_IN_HYBRID = "Plug-in Hybrid (PHEV)"
#     HYBRID = "Hybrid (HEV)"


# class Vehicle(BaseModel):
#     fuel_type: FuelTypeEnum
#     kms_per_week: int


# class Solar(BaseModel):
#     has_solar: bool
#     size: int


# class Battery(BaseModel):
#     fuel_type: FuelTypeEnum
#     kms_per_week: int


# class Household(BaseModel):
#     location: LocationEnum
#     occupancy: conint(ge=1, le=100)
#     space_heater: SpaceHeaterEnum
#     water_heater: WaterHeaterEnum
#     cooktop: CooktopEnum
#     vehicles: List[Vehicle]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/savings", response_model=None) 
def calculate_household_savings(household: Household):
    savings = {
        "emissions": {
            "perWeek": {
                "before": 500.5,
                "after": 100.1,
                "difference": 400.4
            },
            "perYear": {
                "before": 500.5*52,
                "after": 100.1*52,
                "difference": 400.4*52
            },
            "overLifetime": {
                "before": 500.5*52*15*1.1, # some random factor
                "after": 100.1*52*15*1.1,
                "difference": 400.4*52*15*1.1
            },
            "operationalLifetime": 15
        },
        "opex": {
            "perWeek": {
                "before": 300.52,
                "after": 140.11,
                "difference": 160.41
            },
            "perYear": {
                "before": 300.52*52,
                "after": 140.11*52,
                "difference": 160.41*52
            },
            "overLifetime": {
                "before": 300.52*52*15*1.1, # some random factor
                "after": 140.11*52*15*1.1,
                "difference": 160.41*52*15*1.1
            },
            "operationalLifetime": 15
        },
        "upfrontCost": 12345.67
    }
    savingsCls = Savings.from_dict(savings)
    return savingsCls
