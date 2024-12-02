from openapi_client.models.location_enum import LocationEnum

# % of solar that is self-consumed
MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE = {
    "appliances": 0.5,
    "vehicles": 0.5,
    "other_appliances": 0.5,
}

# $/kWh
SOLAR_FEEDIN_TARIFF_2024 = 0.135
SOLAR_FEEDIN_TARIFF_AVG_15_YEARS = 0.14632  # real pricing

# % of max capacity that it generates on average over 30 years, taking into account degradation
SOLAR_AVG_DEGRADED_PERFORMANCE_30_YRS = 0.9308

# Solar capacity factor
SOLAR_CAPACITY_FACTOR = {
    LocationEnum.NORTHLAND: 0.155,
    LocationEnum.AUCKLAND_NORTH: 0.155,
    LocationEnum.AUCKLAND_CENTRAL: 0.155,
    LocationEnum.AUCKLAND_EAST: 0.155,
    LocationEnum.AUCKLAND_WEST: 0.155,
    LocationEnum.AUCKLAND_SOUTH: 0.155,
    LocationEnum.WAIKATO: 0.155,
    LocationEnum.BAY_OF_PLENTY: 0.155,
    LocationEnum.GISBORNE: 0.15,
    LocationEnum.HAWKES_BAY: 0.15,
    LocationEnum.TARANAKI: 0.15,
    LocationEnum.MANAWATU_WANGANUI: 0.15,
    LocationEnum.WELLINGTON: 0.149,
    LocationEnum.TASMAN: 0.15,
    LocationEnum.NELSON: 0.155,
    LocationEnum.MARLBOROUGH: 0.15,
    LocationEnum.WEST_COAST: 0.15,
    LocationEnum.CANTERBURY: 0.143,
    LocationEnum.OTAGO: 0.125,
    LocationEnum.SOUTHLAND: 0.125,
    LocationEnum.STEWART_ISLAND: 0.125,
    LocationEnum.CHATHAM_ISLANDS: 0.125,
    LocationEnum.GREAT_BARRIER_ISLAND: 0.15,
    LocationEnum.OVERSEAS: 0.15,
    LocationEnum.OTHER: 0.15,
}
