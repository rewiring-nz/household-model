from aenum import Enum


class FuelTypeEnum(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    NATURAL_GAS = "NATURAL_GAS"
    LPG = "LPG"
    WOOD = "WOOD"
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    SOLAR = "SOLAR"  # this is direct solar, e.g. roof solar water heaters


# https://environment.govt.nz/assets/publications/Measuring-Emissions-Guidance_EmissionFactors_Summary_2023_ME1781.pdf
# Unit: kgCO2e/kWh
EMISSIONS_FACTORS = {
    "electricity": 0.074,
    "natural_gas": 0.201,
    "lpg": 0.219,
    "wood": 0.016,
    "petrol": 0.258,
    "diesel": 0.253,
    "solar": 0,
}

# From 'Energy prices' C7:C18
# Unit: $/kWh
# https://docs.google.com/spreadsheets/d/1_eAAx5shTHSJAUuHdfj7AQafS0BZJn_0F48yngCpFXI/edit?gid=901618629#gid=901618629
COST_PER_FUEL_KWH_TODAY = {
    "electricity": 0.262,
    "natural_gas": 0.118,
    "lpg": 0.255,
    "wood": 0.113,
    "petrol": 0.289,
    "diesel": 0.197,
    "solar": 0,
}
# TODO: Use this price when doing lifetime opex calculations
# TODO: Update this with average or nominal price for next 15 years from https://docs.google.com/spreadsheets/d/1_eAAx5shTHSJAUuHdfj7AQafS0BZJn_0F48yngCpFXI/edit?gid=901618629#gid=901618629
COST_PER_FUEL_KWH_AVG_15_YEARS = {
    "electricity": 0.282,
    "natural_gas": 0.123,
    "lpg": 0.273,
    "wood": 0.112,
    "petrol": 0.273,
    "diesel": 0.206,
    "solar": 0,
}
