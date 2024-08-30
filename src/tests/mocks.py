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

mock_solar = Solar(has_solar=False, siz=7, install_solar=True)
mock_battery = Battery(has_battery=False, capacity=13, install_battery=True)

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
