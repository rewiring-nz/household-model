import pandas as pd
import pytest
from savings.emissions.calculate_emissions import (
    get_cooktop_emissions_savings,
    get_water_heating_emissions_savings,
    get_vehicle_emissions_savings,
)
from tests.process_test_data import get_test_data


# ============ OLD ============

# Assumes electricity emission factor of 0.098 (not 100% renewable grid)


class TestWaterHeating:
    def test_it_returns_none_for_dont_know(self):
        assert get_water_heating_emissions_savings("Don’t know") == (None, None)

    def test_it_calculates_correctly(self):
        assert get_water_heating_emissions_savings("Gas water heating") == (
            6.88 * 0.217,
            6.88 * 0.217 - 2.07 * 0.098,
        )

    def test_it_does_not_replace_existing_electric(self):
        assert get_water_heating_emissions_savings(
            "Electric (tank/cylinder, also known as ‘resistive’)"
        ) == (
            7.26 * 0.098,
            0,
        )

    def test_it_sets_savings_to_zero_for_solar(self):
        assert get_water_heating_emissions_savings("Solar water heating") == (
            2.07 * 0.098,
            0,
        )


class TestCooktop:
    types_base = {
        "Cooktop_Gas cooktop": 0,
        "Cooktop_LPG cooktop": 0,
        "Cooktop_Electric resistance cooktop": 0,
        "Cooktop_Electric induction cooktop": 0,
        "Cooktop_Don't know": 0,
    }

    def test_it_does_not_replace_electric(self):
        electric = pd.Series(
            {
                **self.types_base,
                "Cooktop_Electric resistance cooktop": 1,
                "Cooktop_Electric induction cooktop": 1,
            }
        )
        assert get_cooktop_emissions_savings(electric) == (
            0.89 * 0.098 + 0.81 * 0.098,
            0,
        )

    def test_it_returns_nones_for_dont_know(self):
        dont_know = pd.Series(
            {
                **self.types_base,
                "Cooktop_Don't know": 1,
            }
        )
        assert get_cooktop_emissions_savings(dont_know) == (None, None)

    def test_it_calculates_savings_correctly(self):
        gas = pd.Series(
            {
                **self.types_base,
                "Cooktop_Gas cooktop": 1,
            }
        )
        assert get_cooktop_emissions_savings(gas) == (
            2.08 * 0.217,
            2.08 * 0.217 - 0.81 * 0.098,
        )

        lpg = pd.Series(
            {
                **self.types_base,
                "Cooktop_LPG cooktop": 1,
            }
        )
        assert get_cooktop_emissions_savings(lpg) == (
            2.08 * 0.218,
            2.08 * 0.218 - 0.81 * 0.098,
        )

        gas_and_lpg = pd.Series(
            {
                **self.types_base,
                "Cooktop_Gas cooktop": 1,
                "Cooktop_LPG cooktop": 1,
            }
        )
        assert get_cooktop_emissions_savings(gas_and_lpg) == (
            2.08 * 0.217 + 2.08 * 0.218,
            (2.08 * 0.217 - 0.81 * 0.098) + (2.08 * 0.218 - 0.81 * 0.098),
        )

    def test_it_handles_some_electric_some_not(self):
        mixed = pd.Series(
            {
                **self.types_base,
                "Cooktop_Electric resistance cooktop": 1,
                "Cooktop_Electric induction cooktop": 1,
                "Cooktop_Gas cooktop": 1,
            }
        )
        expected_emissions = 0.89 * 0.098 + 0.81 * 0.098 + 2.08 * 0.217
        assert get_cooktop_emissions_savings(mixed) == (
            expected_emissions,
            2.08 * 0.217 - 0.81 * 0.098,
        )


# TODO: mock out extract_vehicle_stats
class TestVehicles:
    base = {
        "Vehicles": 0,
        "Vehicles fuel/energy type_Vehicle 1": None,
        "Vehicles fuel/energy type_Vehicle 2": None,
        "Vehicles fuel/energy type_Vehicle 3": None,
        "Vehicles fuel/energy type_Vehicle 4": None,
        "Vehicles fuel/energy type_Vehicle 5": None,
        "Vehicles distance_Vehicle 1": None,
        "Vehicles distance_Vehicle 2": None,
        "Vehicles distance_Vehicle 3": None,
        "Vehicles distance_Vehicle 4": None,
        "Vehicles distance_Vehicle 5": None,
    }
    petrol_running = 32 * 0.242
    # petrol_embodied = 6700 / 15 / 365.25
    petrol_embodied = 0

    diesel_running = 28.4 * 0.253
    # diesel_embodied = 7000 / 15 / 365.25
    diesel_embodied = 0

    ev_running = 8.027 * 0.098
    # ev_embodied = 11100 / 15 / 365.25
    ev_embodied = 0

    plugin_running = petrol_running * 0.6 + ev_running * 0.4
    plugin_embodied = petrol_embodied * 0.6 + ev_embodied * 0.4

    hybrid_running = petrol_running * 0.7 + ev_running * 0.3
    hybrid_embodied = petrol_embodied * 0.7 + ev_embodied * 0.3

    def test_it_returns_zeros_if_no_vehicle(self):
        assert get_vehicle_emissions_savings(pd.Series(self.base)) == (0, 0)

    def test_it_returns_zeros_if_not_sure(self):
        assert get_vehicle_emissions_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 1,
                    "Vehicles fuel/energy type_Vehicle 1": "I’m not sure",
                }
            )
        ) == (0, 0)

    def test_it_returns_emissions_savings_for_one_petrol_vehicle(self):
        household = pd.Series(
            {
                **self.base,
                "Vehicles": 1,
                "Vehicles fuel/energy type_Vehicle 1": "Petrol",
                "Vehicles distance_Vehicle 1": "100-199km",
            }
        )
        # petrol car
        distance_per_week = 150  # taking the middle of the 100-199km range
        distance_per_year = distance_per_week * 52
        pct_of_avg = distance_per_year / 11000
        emissions_before = self.petrol_running * pct_of_avg + self.petrol_embodied
        emissions_after = self.ev_running * pct_of_avg + self.ev_embodied
        assert get_vehicle_emissions_savings(household) == (
            emissions_before,
            emissions_before - emissions_after,
        )

    def test_it_uses_average_distance_if_not_sure(self):
        household = pd.Series(
            {
                **self.base,
                "Vehicles": 1,
                "Vehicles fuel/energy type_Vehicle 1": "Petrol",
                "Vehicles distance_Vehicle 1": "I’m not sure",
            }
        )
        # petrol car
        emissions_before = self.petrol_running + self.petrol_embodied
        emissions_after = self.ev_running + self.ev_embodied
        assert get_vehicle_emissions_savings(household) == (
            emissions_before,
            emissions_before - emissions_after,
        )

    def test_it_returns_emissions_savings_for_multiple_ff_vehicles(self):
        total_emissions, total_savings = get_vehicle_emissions_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 3,
                    "Vehicles fuel/energy type_Vehicle 1": "Petrol",
                    "Vehicles fuel/energy type_Vehicle 2": "Petrol",
                    "Vehicles fuel/energy type_Vehicle 3": "Diesel",
                    "Vehicles distance_Vehicle 1": "0-50km",
                    "Vehicles distance_Vehicle 2": "100-199km",
                    "Vehicles distance_Vehicle 3": "200+ km",
                }
            )
        )
        expected_total_emissions = (
            (self.petrol_running * 25 * 52 / 11000 + self.petrol_embodied)
            + (self.petrol_running * 150 * 52 / 11000 + self.petrol_embodied)
            + (self.diesel_running * 250 * 52 / 11000 + self.diesel_embodied)
        )
        assert total_emissions == expected_total_emissions
        expected_total_savings = expected_total_emissions - (
            (self.ev_running * 25 * 52 / 11000 + self.ev_embodied)
            + (self.ev_running * 150 * 52 / 11000 + self.ev_embodied)
            + (self.ev_running * 250 * 52 / 11000 + self.ev_embodied)
        )
        assert total_savings == pytest.approx(expected_total_savings)

    def test_it_calculates_correctly_for_PHEV(self):
        emissions, savings = get_vehicle_emissions_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 1,
                    "Vehicles fuel/energy type_Vehicle 1": "Plug-in Hybrid",
                    "Vehicles distance_Vehicle 1": "0-50km",
                }
            )
        )
        expected_emissions = (
            self.plugin_running * 25 / 11000 * 52 + self.plugin_embodied
        )
        assert emissions == expected_emissions
        assert savings == expected_emissions - (
            self.ev_running * 25 / 11000 * 52 + self.ev_embodied
        )

    def test_it_calculates_correctly_for_HEV(self):
        emissions, savings = get_vehicle_emissions_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 1,
                    "Vehicles fuel/energy type_Vehicle 1": "Hybrid",
                    "Vehicles distance_Vehicle 1": "0-50km",
                }
            )
        )
        expected_emissions = (
            self.hybrid_running * 25 / 11000 * 52 + self.hybrid_embodied
        )
        assert emissions == pytest.approx(expected_emissions)
        assert savings == pytest.approx(
            expected_emissions - (self.ev_running * 25 / 11000 * 52 + self.ev_embodied)
        )

    def test_it_does_not_switch_for_electric_vehicles(self):
        total_emissions, total_savings = get_vehicle_emissions_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 3,
                    "Vehicles fuel/energy type_Vehicle 1": "Petrol",
                    "Vehicles fuel/energy type_Vehicle 2": "Electric",
                    "Vehicles fuel/energy type_Vehicle 3": "Plug-in Hybrid",  # PHEVs are still switched
                    "Vehicles distance_Vehicle 1": "0-50km",
                    "Vehicles distance_Vehicle 2": "100-199km",
                    "Vehicles distance_Vehicle 3": "200+ km",
                }
            )
        )
        expected_total_emissions = (
            (self.petrol_running * 25 * 52 / 11000 + self.petrol_embodied)
            + (self.ev_running * 150 * 52 / 11000 + self.ev_embodied)
            + (self.plugin_running * 250 * 52 / 11000 + self.plugin_embodied)
        )
        assert total_emissions == expected_total_emissions
        expected_total_savings = expected_total_emissions - (
            (self.ev_running * 25 * 52 / 11000 + self.ev_embodied)
            + (self.ev_running * 150 * 52 / 11000 + self.ev_embodied)
            + (self.ev_running * 250 * 52 / 11000 + self.ev_embodied)
        )
        assert total_savings == pytest.approx(expected_total_savings)

    def test_complex_example(self):
        total_emissions, total_savings = get_vehicle_emissions_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 4,
                    "Vehicles fuel/energy type_Vehicle 1": "Petrol",
                    "Vehicles fuel/energy type_Vehicle 2": "Petrol",
                    "Vehicles fuel/energy type_Vehicle 3": "Diesel",
                    "Vehicles fuel/energy type_Vehicle 4": "Hybrid",
                    "Vehicles distance_Vehicle 1": "0-50km",
                    "Vehicles distance_Vehicle 2": "0-50km",
                    "Vehicles distance_Vehicle 3": "0-50km",
                    "Vehicles distance_Vehicle 4": "0-50km",
                }
            )
        )
        expected_total_emissions = (
            (self.petrol_running * 25 * 52 / 11000 + self.petrol_embodied) * 2
            + (self.diesel_running * 25 * 52 / 11000 + self.diesel_embodied)
            + (self.hybrid_running * 25 * 52 / 11000 + self.hybrid_embodied)
        )
        assert total_emissions == expected_total_emissions
        expected_total_savings = expected_total_emissions - (
            (self.ev_running * 25 * 52 / 11000 + self.ev_embodied) * 4
        )
        assert total_savings == pytest.approx(expected_total_savings)
