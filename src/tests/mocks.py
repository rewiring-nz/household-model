from openapi_client.models import (
    Household,
    Savings,
    Emissions,
    EmissionsValues,
    Opex,
    OpexValues,
    UpfrontCost,
    Recommendation,
    RecommendationActionEnum,
    Vehicle,
    LocationEnum,
    SpaceHeatingEnum,
    WaterHeatingEnum,
    CooktopEnum,
    VehicleFuelTypeEnum,
    Solar,
    Battery,
)

mock_vehicle_petrol = Vehicle(
    fuel_type=VehicleFuelTypeEnum.PETROL,
    kms_per_week=250,
    switch_to_ev=True,
)
mock_vehicle_diesel = Vehicle(
    fuel_type=VehicleFuelTypeEnum.DIESEL,
    kms_per_week=50,
    switch_to_ev=False,
)

mock_solar = Solar(has_solar=False, size=7, install_solar=True)
mock_battery = Battery(has_battery=False, capacity=13, install_battery=False)

mock_household = Household(
    **{
        "location": LocationEnum.AUCKLAND_CENTRAL,
        "occupancy": 4,
        "space_heating": SpaceHeatingEnum.WOOD,
        "water_heating": WaterHeatingEnum.GAS,
        "cooktop": CooktopEnum.ELECTRIC_RESISTANCE,
        "vehicles": [
            mock_vehicle_petrol,
            mock_vehicle_diesel,
        ],
        "solar": mock_solar,
        "battery": mock_battery,
    }
)

mock_household_electrified = Household(
    **{
        "location": LocationEnum.AUCKLAND_CENTRAL,
        "occupancy": 4,
        "space_heating": SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
        "water_heating": WaterHeatingEnum.ELECTRIC_HEAT_PUMP,
        "cooktop": CooktopEnum.ELECTRIC_RESISTANCE,  # don't swap if already electric
        "vehicles": [
            Vehicle(
                fuel_type=VehicleFuelTypeEnum.ELECTRIC,
                kms_per_week=250,
                switch_to_ev=None,
            ),
            mock_vehicle_diesel,  # did not want to switch this one
        ],
        "solar": Solar(has_solar=True, size=7, install_solar=None),
        "battery": Battery(
            has_battery=False, capacity=13, install_battery=False
        ),  # Did not want a battery
    }
)

mock_emissions = Emissions(
    perWeek=EmissionsValues(before=500.5, after=100.1, difference=400.4),
    perYear=EmissionsValues(before=500.5 * 52, after=100.1 * 52, difference=400.4 * 52),
    overLifetime=EmissionsValues(
        before=500.5 * 52 * 15 * 1.1,  # some random factor
        after=100.1 * 52 * 15 * 1.1,
        difference=400.4 * 52 * 15 * 1.1,
    ),
    operationalLifetime=15,
)

mock_opex = Opex(
    perWeek=OpexValues(before=300.52, after=140.11, difference=160.41),
    perYear=OpexValues(before=300.52 * 52, after=140.11 * 52, difference=160.41 * 52),
    overLifetime=OpexValues(
        before=300.52 * 52 * 15 * 1.1,  # some random factor
        after=140.11 * 52 * 15 * 1.1,
        difference=160.41 * 52 * 15 * 1.1,
    ),
    operationalLifetime=15,
)

mock_upfront_cost = UpfrontCost(
    solar=15000.12,
    battery=7000.31,
    cooktop=500.50,
    waterHeating=3000.15,
    spaceHeating=3300.12,
)

mock_recommendation = Recommendation(
    action=RecommendationActionEnum("SPACE_HEATING"),
    url="https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
)
