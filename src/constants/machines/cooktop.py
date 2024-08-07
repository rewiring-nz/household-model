# Cooktops kWh/day
# From 'Machines'!D192
COOKTOP_COLS = [
    "Cooktop_Gas cooktop",
    "Cooktop_LPG cooktop",
    "Cooktop_Electric resistance cooktop",
    "Cooktop_Electric induction cooktop",
    "Cooktop_Don't know",
]

COOKTOP_KWH_PER_DAY = {
    "Cooktop_Gas cooktop": 2.08,
    "Cooktop_LPG cooktop": 2.08,
    "Cooktop_Electric resistance cooktop": 0.89,
    "Cooktop_Electric induction cooktop": 0.81,
}

COOKTOP_ELECTRIC_TYPES = [
    "Cooktop_Electric resistance cooktop",
    "Cooktop_Electric induction cooktop",
]

COOKTOP_TYPE_TO_FUEL_TYPE = {
    "Cooktop_Gas cooktop": 'natural_gas',
    "Cooktop_LPG cooktop": 'lpg',
    "Cooktop_Electric resistance cooktop": 'electricity',
    "Cooktop_Electric induction cooktop": 'electricity',
}

# From 'Machines'!D196
# Do NOT including fixed cost proportion, this is calculated separately
COOKTOP_OPEX_15_YRS = {
    "Cooktop_Gas cooktop": 1426.9,
    "Cooktop_LPG cooktop": 3166.6,
    "Cooktop_Electric resistance cooktop": 1402.7,
    "Cooktop_Electric induction cooktop": 1270,
}

# From 'Product prices'!D25:D27
COOKTOP_UPFRONT_COST = {
    "Cooktop_Gas cooktop": {
        "item_price": 1022,
        "install_cost": 630,
    },
    "Cooktop_LPG cooktop": {
        "item_price": 1022,
        "install_cost": 630,
    },
    "Cooktop_Electric resistance cooktop": {
        "item_price": 879,
        "install_cost": 288,
    },
    "Cooktop_Electric induction cooktop": {
        "item_price": 1430,
        "install_cost": 1265,
    },
}
