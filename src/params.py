from constants.fuel_stats import EMISSIONS_FACTORS, COST_PER_FUEL_KWH_TODAY
from constants.machines.cooktop import (
    COOKTOP_KWH_PER_DAY,
    COOKTOP_OPEX_15_YRS,
    COOKTOP_TYPE_TO_FUEL_TYPE,
)
from constants.machines.water_heating import (
    WATER_HEATING_KWH_PER_DAY,
    WATER_HEATING_OPEX_15_YRS,
    WATER_HEATING_TYPE_TO_FUEL_TYPE,
)
from constants.machines.vehicles import (
    VEHICLE_KWH_PER_DAY,
    VEHICLE_OPEX_15_YRS,
    VEHICLE_EMBODIED_EMISSIONS,
    VEHICLE_OPEX_PER_DAY,
)

OPERATIONAL_LIFETIME = 15

# ============ OLD ============

HOUSEHOLD_ENERGY_USE = 1  # % of average
SOLAR_SIZE = 5  # kW

# Change the type of machine that households should switch to here:

SWITCH_TO = {
    "space_heating": {
        "switch_to_type": "Home heating_Heat pump split system (an individual unit in a room(s))",
        # Assume resistive heaters are swapped for heat pumps; cost savings will be worth it, even if emisisons savings are minor.
        "switch_if_electric": True,
    },
    "water_heating": {
        "switch_to_type": "Heat pump electric",
        # Assume that if they're already on some form of electric water heater,
        # they're not going to switch to specifically heat pump electric
        "switch_if_electric": False,
    },
    "cooktop": {
        "switch_to_type": "Cooktop_Electric induction cooktop",
        "switch_if_electric": False,
    },
    "vehicle": {
        "switch_to_type": "Electric",
        "switch_if_electric": False,
    },
}

# Home heating


# Water heating

WATER_HEATING_SWITCH_TO_EMISSIONS = (
    WATER_HEATING_KWH_PER_DAY[SWITCH_TO["water_heating"]["switch_to_type"]]
    * EMISSIONS_FACTORS["electricity"]
)
WATER_HEATING_SWITCH_TO_OPEX = (
    WATER_HEATING_KWH_PER_DAY[SWITCH_TO["water_heating"]["switch_to_type"]]
    * COST_PER_FUEL_KWH_TODAY[
        WATER_HEATING_TYPE_TO_FUEL_TYPE[SWITCH_TO["water_heating"]["switch_to_type"]]
    ]
    * 365.25
    * OPERATIONAL_LIFETIME
)

# Cooktop

COOKTOP_SWITCH_TO_EMISSIONS = (
    COOKTOP_KWH_PER_DAY[SWITCH_TO["cooktop"]["switch_to_type"]]
    * EMISSIONS_FACTORS["electricity"]
)
COOKTOP_SWITCH_TO_OPEX = (
    COOKTOP_KWH_PER_DAY[SWITCH_TO["cooktop"]["switch_to_type"]]
    * COST_PER_FUEL_KWH_TODAY[
        COOKTOP_TYPE_TO_FUEL_TYPE[SWITCH_TO["cooktop"]["switch_to_type"]]
    ]
    * 365.25
    * OPERATIONAL_LIFETIME
)

# Vehicle

VEHICLE_SWITCH_TO_EMISSIONS_RUNNING = (
    VEHICLE_KWH_PER_DAY[SWITCH_TO["vehicle"]["switch_to_type"]]
    * EMISSIONS_FACTORS["electricity"]
)
VEHICLE_SWITCH_TO_EMISSIONS_EMBODIED = (
    VEHICLE_EMBODIED_EMISSIONS[SWITCH_TO["vehicle"]["switch_to_type"]]
    / OPERATIONAL_LIFETIME
    / 365.25
)
VEHICLE_SWITCH_TO_OPEX_FUEL = VEHICLE_OPEX_PER_DAY[
    SWITCH_TO["vehicle"]["switch_to_type"]
]

VEHICLE_SWITCH_TO_OPEX = VEHICLE_OPEX_15_YRS[SWITCH_TO["vehicle"]["switch_to_type"]]
