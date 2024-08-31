# Other machines (space cooling, refrigeration, laundry, lighting, etc.)

ENERGY_NEEDS_SPACE_COOLING = 0.34  # kWh per day, Machines!D113
ENERGY_NEEDS_OTHER_APPLIANCES = 4.48  # kWh per day, Machines!C244
ENERGY_NEEDS_OTHER_COOKING = 3.06  # kWh per day, Machines!C224

ENERGY_NEEDS_OTHER_MACHINES_PER_DAY = (
    ENERGY_NEEDS_SPACE_COOLING
    + ENERGY_NEEDS_OTHER_APPLIANCES
    + ENERGY_NEEDS_OTHER_COOKING
)  # kWh per day
