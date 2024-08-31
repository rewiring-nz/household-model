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
# Unit: kgCO2e/kWh
EMISSIONS_FACTORS = {
    "electricity": 0.098,
    # 'electricity': 0.0,  # assuming 100% renewable grid
    "natural_gas": 0.217,
    "lpg": 0.218,
    "wood": 0.025,
    "petrol": 0.242,
    "diesel": 0.253,
    "solar": 0,
    # Excluding coal for now, as it skews results
    # 'coal': 0.9,  # TODO: check this, UK source from https://www.rensmart.com/Calculators/KWH-to-CO2
}

# From 'Energy prices'
# Unit: $/kWh
COST_PER_FUEL_KWH_TODAY = {
    "electricity": 0.242,  # today's grid average flat, G14
    "natural_gas": 0.11,  # C45
    "lpg": 0.244,  # C51
    "wood": 0.113,  # C54
    "petrol": 0.27,  # C57
    "diesel": 0.21,  # C58
    "solar": 0,
}
# TODO: Use this price when doing lifetime opex calculations
COST_PER_FUEL_KWH_AVG_15_YEARS = {
    "electricity": 0.282,
    "natural_gas": 0.123,
    "lpg": 0.273,
    "wood": 0.112,
    "petrol": 0.273,
    "diesel": 0.206,
    "solar": 0,
}
