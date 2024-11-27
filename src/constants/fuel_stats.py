from aenum import Enum


class FuelTypeEnum(str, Enum):
    ELECTRICITY = "electricity"
    NATURAL_GAS = "natural_gas"
    LPG = "lpg"
    WOOD = "wood"
    PETROL = "petrol"
    DIESEL = "diesel"
    SOLAR = "solar"  # this is direct solar, e.g. roof solar water heaters


# From 'Misc'!B154
# Original source: https://environment.govt.nz/assets/publications/Measuring-Emissions-Guidance_EmissionFactors_Summary_2023_ME1781.pdf
# Unit: kgCO2e/kWh
EMISSIONS_FACTORS = {
    FuelTypeEnum.ELECTRICITY: 0.074,
    FuelTypeEnum.NATURAL_GAS: 0.201,
    FuelTypeEnum.LPG: 0.219,
    FuelTypeEnum.WOOD: 0.016,
    FuelTypeEnum.PETROL: 0.258,
    FuelTypeEnum.DIESEL: 0.253,
    FuelTypeEnum.SOLAR: 0,
}

# 2024 prices from 'Energy prices' C7:C18
# Unit: $/kWh
COST_PER_FUEL_KWH_TODAY = {
    FuelTypeEnum.ELECTRICITY: {
        "volume_rate": 0.26175,
        "off_peak": 0.173,
    },
    FuelTypeEnum.NATURAL_GAS: 0.118,
    FuelTypeEnum.LPG: 0.25452,
    FuelTypeEnum.WOOD: 0.11250,
    FuelTypeEnum.PETROL: 0.28884,
    FuelTypeEnum.DIESEL: 0.19679,
    FuelTypeEnum.SOLAR: 0,
}

# Average over next 15 years (real)
# Unit: $/kWh
COST_PER_FUEL_KWH_AVG_15_YEARS = {
    FuelTypeEnum.ELECTRICITY: {
        "volume_rate": 0.29515,
        "off_peak": 0.19507,
    },
    FuelTypeEnum.NATURAL_GAS: 0.14161,
    FuelTypeEnum.LPG: 0.30544,
    FuelTypeEnum.WOOD: 0.12837,
    FuelTypeEnum.PETROL: 0.36584,
    FuelTypeEnum.DIESEL: 0.24925,
    FuelTypeEnum.SOLAR: 0,
}

FIXED_COSTS_PER_YEAR_2024 = {
    FuelTypeEnum.ELECTRICITY: 767.7555,
    FuelTypeEnum.NATURAL_GAS: 689.22675,
    FuelTypeEnum.LPG: 69,
}

FIXED_COSTS_PER_YEAR_AVG_15_YEARS = {
    FuelTypeEnum.ELECTRICITY: 865.71,
    FuelTypeEnum.NATURAL_GAS: 827.10,
    FuelTypeEnum.LPG: 82.803,
}
