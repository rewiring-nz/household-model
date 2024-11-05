# Other machines (space cooling, refrigeration, laundry, lighting, etc.)

ENERGY_NEEDS_SPACE_COOLING = 0.34  # kWh per day, Machines!D113
ENERGY_NEEDS_OTHER_APPLIANCES = 4.05  # kWh per day, Machines!C2448  Lights (0.64), washing machine (0.25), dryer (0.11), other incl TVs/computers etc. (3.05)
ENERGY_NEEDS_OTHER_COOKING = 2.85  # kWh per day, Machines!C228. Oven (0.47), microwave (0.25), refrigeration (1.88), dishwasher (0.24)

ENERGY_NEEDS_OTHER_MACHINES_PER_DAY = (
    ENERGY_NEEDS_SPACE_COOLING
    + ENERGY_NEEDS_OTHER_APPLIANCES
    + ENERGY_NEEDS_OTHER_COOKING
)  # kWh per day
