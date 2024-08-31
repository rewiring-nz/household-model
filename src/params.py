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
