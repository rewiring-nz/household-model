# Water heating kWh/day
# From 'Machines'!D137 (rounded to 2dp)
WATER_HEATING_KWH_PER_DAY = {
    'Electric (tank/cylinder, also known as ‘resistive’)': 7.26,  # G137, "If resistive (& ripple control)"
    'Gas water heating': 6.88,
    'LPG water heating': 6.88,
    'Heat pump electric': 2.07,  # I137, "If heat pump on grid"
    'Solar water heating': 2.07,  # J137, roughly same as heat pump electric
    'Diesel water heating': 9.01,
}

WATER_HEATING_ELECTRIC_TYPES = [
    'Electric (tank/cylinder, also known as ‘resistive’)',
    'Heat pump electric',
    'Solar water heating',
]

WATER_HEATING_TYPE_TO_FUEL_TYPE = {
    'Electric (tank/cylinder, also known as ‘resistive’)': 'electricity',
    'Gas water heating': 'natural_gas',
    'LPG water heating': 'lpg',
    'Heat pump electric': 'electricity',
    'Solar water heating': 'electricity',
    'Diesel water heating': 'diesel',
}


# From 'Machines'
# Energy costs (15yr) (D141) - do NOT including fixed cost proportion, this is calculated separately
WATER_HEATING_OPEX_15_YRS = {
    'Electric (tank/cylinder, also known as ‘resistive’)': 7160,  # "If resistive (& ripple control)"
    'Gas water heating': 4714,
    'LPG water heating': 10463,
    'Heat pump electric': 3269,
    'Solar water heating': 3269,  # a specific type of heating on the roof that isn't very popular anymore. Don't use R141, which is a house with solar panels + heat pump, a different thing. Assume same as heat pump electric.
    'Diesel water heating': 10234,
}

# From 'Product prices'!D17:D21
WATER_HEATING_UPFRONT_COST = {
    'Electric (tank/cylinder, also known as ‘resistive’)': {
        "item_price": 1975,  # C18 (assuming large size since average of heat pump list is around 300L)
        "install_cost": 1995,  # D18
    },
    'Gas water heating': {
        "item_price": 1418,  # C20
        "install_cost": 2175,  # D20
    },
    'LPG water heating': {
        "item_price": 1419,  # C21
        "install_cost": 2175,  # D21
    },
    'Heat pump electric': {
        "item_price": 4678,  # C17
        "install_cost": 2321,  # D17
    },
}
