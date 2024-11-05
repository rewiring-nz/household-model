from aenum import Enum


class FuelTypeEnum(str, Enum):
    ELECTRICITY = "electricity"
    NATURAL_GAS = "natural_gas"
    LPG = "lpg"
    WOOD = "wood"
    PETROL = "petrol"
    DIESEL = "diesel"
    SOLAR = "solar"  # this is direct solar, e.g. roof solar water heaters


# TODO: key the following dicts on FuelTypeEnum as the key, rather than its value
# From 'Misc'!B154
# Original source: https://environment.govt.nz/assets/publications/Measuring-Emissions-Guidance_EmissionFactors_Summary_2023_ME1781.pdf
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

# 2024 prices from 'Energy prices' C7:C18
# Unit: $/kWh
# TODO: key these with FuelTypeEnum
COST_PER_FUEL_KWH_TODAY = {
    "electricity": {
        "volume_rate": 0.26175,
        "off_peak": 0.173,
    },
    "natural_gas": 0.118,
    "lpg": 0.25452,
    "wood": 0.11250,
    "petrol": 0.28884,
    "diesel": 0.19679,
    "solar": 0,
}

# Average over next 15 years (real)
# TODO: Use this price when doing lifetime opex calculations
# Unit: $/kWh
COST_PER_FUEL_KWH_AVG_15_YEARS = {
    "electricity": {
        "volume_rate": 0.29515,
        "off_peak": 0.19507,
    },
    "natural_gas": 0.14161,
    "lpg": 0.30544,
    "wood": 0.12837,
    "petrol": 0.36584,
    "diesel": 0.24925,
    "solar": 0,
}

FIXED_COSTS_PER_YEAR_2024 = {
    FuelTypeEnum.ELECTRICITY: 767.7555,
    FuelTypeEnum.NATURAL_GAS: 689.22675,
    FuelTypeEnum.LPG: 69,
}

FIXED_COSTS_PER_YEAR_AVG_15_YEARS = {
    FuelTypeEnum.ELECTRICITY: 865.70526,
    FuelTypeEnum.NATURAL_GAS: 827.10354,
    FuelTypeEnum.LPG: 82.80315,
}
