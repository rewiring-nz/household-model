import pandas as pd
from constants.machines.vehicles import extract_vehicle_stats
from tests.process_test_data import get_test_data

base_household = get_test_data('tests/base_household.csv')


def test_extract_vehicle_stats_with_no_vehicles():
    household = pd.Series(
        {
            **base_household,
            'Vehicles': 0,
        }
    )
    result = extract_vehicle_stats(household)
    assert result == []


def test_extract_vehicle_stats_with_one_vehicle():
    household = pd.Series(
        {
            **base_household,
            'Vehicles': 1,
            'Vehicles fuel/energy type_Vehicle 1': 'Petrol',
            'Vehicles fuel/energy type_Vehicle 2': None,
            'Vehicles fuel/energy type_Vehicle 3': None,
            'Vehicles fuel/energy type_Vehicle 4': None,
            'Vehicles fuel/energy type_Vehicle 5': None,
            'Vehicles distance_Vehicle 1': '50-99km',
            'Vehicles distance_Vehicle 2': None,
            'Vehicles distance_Vehicle 3': None,
            'Vehicles distance_Vehicle 4': None,
            'Vehicles distance_Vehicle 5': None,
        }
    )
    result = extract_vehicle_stats(household)
    assert result == [{'fuel_type': 'Petrol', 'distance_per_yr': 75 * 52}]


def test_extract_vehicle_stats_ignores_unsure_fuel_types():
    household = pd.Series(
        {
            **base_household,
            'Vehicles': 2,
            'Vehicles fuel/energy type_Vehicle 1': 'I’m not sure',
            'Vehicles fuel/energy type_Vehicle 2': 'Electric',
            'Vehicles fuel/energy type_Vehicle 3': None,
            'Vehicles fuel/energy type_Vehicle 4': None,
            'Vehicles fuel/energy type_Vehicle 5': None,
            'Vehicles distance_Vehicle 1': '50-99km',
            'Vehicles distance_Vehicle 2': '200+ km',
            'Vehicles distance_Vehicle 3': None,
            'Vehicles distance_Vehicle 4': None,
            'Vehicles distance_Vehicle 5': None,
        }
    )
    result = extract_vehicle_stats(household)
    assert result == [
        {'fuel_type': 'Electric', 'distance_per_yr': 250 * 52},
    ]


def test_extract_vehicle_stats_with_multiple_vehicles():
    household = pd.Series(
        {
            **base_household,
            'Vehicles': 2,
            'Vehicles fuel/energy type_Vehicle 1': 'Petrol',
            'Vehicles fuel/energy type_Vehicle 2': 'Electric',
            'Vehicles fuel/energy type_Vehicle 3': None,
            'Vehicles fuel/energy type_Vehicle 4': None,
            'Vehicles fuel/energy type_Vehicle 5': None,
            'Vehicles distance_Vehicle 1': '50-99km',
            'Vehicles distance_Vehicle 2': '200+ km',
            'Vehicles distance_Vehicle 3': None,
            'Vehicles distance_Vehicle 4': None,
            'Vehicles distance_Vehicle 5': None,
        }
    )
    result = extract_vehicle_stats(household)
    assert result == [
        {'fuel_type': 'Petrol', 'distance_per_yr': 75 * 52},
        {'fuel_type': 'Electric', 'distance_per_yr': 250 * 52},
    ]


def test_extract_vehicle_ignores_anything_past_5():
    household = pd.Series(
        {
            **base_household,
            'Vehicles': 6,
            'Vehicles fuel/energy type_Vehicle 1': 'Petrol',
            'Vehicles fuel/energy type_Vehicle 2': 'Electric',
            'Vehicles fuel/energy type_Vehicle 3': 'Petrol',
            'Vehicles fuel/energy type_Vehicle 4': 'Petrol',
            'Vehicles fuel/energy type_Vehicle 5': 'Petrol',
            'Vehicles distance_Vehicle 1': '50-99km',
            'Vehicles distance_Vehicle 2': '200+ km',
            'Vehicles distance_Vehicle 3': '200+ km',
            'Vehicles distance_Vehicle 4': '200+ km',
            'Vehicles distance_Vehicle 5': '200+ km',
        }
    )
    result = extract_vehicle_stats(household)
    assert result == [
        {'fuel_type': 'Petrol', 'distance_per_yr': 75 * 52},
        {'fuel_type': 'Electric', 'distance_per_yr': 250 * 52},
        {'fuel_type': 'Petrol', 'distance_per_yr': 250 * 52},
        {'fuel_type': 'Petrol', 'distance_per_yr': 250 * 52},
        {'fuel_type': 'Petrol', 'distance_per_yr': 250 * 52},
    ]
