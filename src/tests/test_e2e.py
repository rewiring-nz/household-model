import sys

sys.path.append('../src')
import pandas as pd

from utils.print_results import print_results
from savings.emissions_savings import enrich_emissions
from savings.opex_savings import enrich_opex
from savings.upfront_cost import enrich_upfront_cost

from tests.process_test_data import get_test_data

BASE_HOUSEHOLD = get_test_data('tests/base_household.csv')

GAS_APPLIANCES_PETROL_VEHICLES = pd.DataFrame.from_records(
    [
        {
            **BASE_HOUSEHOLD,
            "Home heating_Gas fireplac(s) (not LPG)": 1,
            "Home heating number_Gas or LPG fireplace": 1,
            "Cooktop_Gas cooktop": 1,
            "Water heating": "Gas water heating",
            # 2 vehicles that go ~210km per week (average)
            "Vehicles": 2,
            "Vehicles fuel/energy type_Vehicle 1": 'Petrol',
            "Vehicles fuel/energy type_Vehicle 2": 'Petrol',
            "Vehicles distance_Vehicle 1": "200+ km",
            # "Vehicles distance_Vehicle 1": "0-50km",
            "Vehicles distance_Vehicle 2": "200+ km",
            # "Vehicles distance_Vehicle 2": "0-50km",
            # Adding extra resistive
            # "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 1,
            # "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 3,
        }
    ]
)


if __name__ == "__main__":
    household = GAS_APPLIANCES_PETROL_VEHICLES
    household = enrich_emissions(household)
    household = enrich_opex(household)
    household = enrich_upfront_cost(household)
    import pdb

    pdb.set_trace()
    print_results(household)
