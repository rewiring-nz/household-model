import pytest
import pandas as pd

from savings.opex.calculate_opex import (
    get_fixed_costs_per_year,
    NGAS_MACHINES,
    LPG_MACHINES,
    get_home_heating_opex_savings,
    get_water_heating_opex_savings,
    get_cooktop_opex_savings,
    get_vehicle_opex_savings,
)
from constants.machines.cooktop import COOKTOP_KWH_PER_DAY
from tests.process_test_data import get_test_data

base_household = get_test_data("tests/base_household.csv")


class TestGetFixedCostSavings:

    def test_it_returns_electric_only_if_no_gas(self):
        assert get_fixed_costs_per_year(
            pd.Series(
                {
                    **base_household,
                    "Home heating_Wood fireplace(s)": 1,
                    "Home heating number_Wood fireplace": 2,
                    "Cooktop_Electric resistance cooktop": 1,
                }
            )
        ) == (689, 0)

    def test_it_returns_fixed_cost_if_one_ngas(self):
        for x in NGAS_MACHINES:
            result = get_fixed_costs_per_year(
                pd.Series(
                    {
                        **base_household,
                        x: 1,
                    }
                )
            )
            assert result == (587 + 689, 587)

        # Water heating is an enum column as opposed to a set of boolean columns
        assert get_fixed_costs_per_year(
            pd.Series(
                {
                    **base_household,
                    "Water heating": "Gas water heating",
                }
            )
        ) == (587 + 689, 587)

    def test_it_returns_same_fixed_cost_for_multiple_ngas(self):
        result = get_fixed_costs_per_year(
            pd.Series(
                {
                    **base_household,
                    **{x: 1 for x in NGAS_MACHINES},
                    "Water heating": "Gas water heating",
                }
            )
        )
        assert result == (587 + 689, 587)

    def test_it_returns_fixed_cost_if_one_lpg(self):
        for x in LPG_MACHINES:
            result = get_fixed_costs_per_year(
                pd.Series(
                    {
                        **base_household,
                        x: 1,
                    }
                )
            )
            assert result == (139 + 689, 139)

        # Water heating is an enum column as opposed to a set of boolean columns
        assert get_fixed_costs_per_year(
            pd.Series(
                {
                    **base_household,
                    "Water heating": "LPG water heating",
                }
            )
        ) == (139 + 689, 139)

    def test_it_returns_same_fixed_cost_for_multiple_lpg(self):
        result = get_fixed_costs_per_year(
            pd.Series(
                {
                    **base_household,
                    **{x: 1 for x in LPG_MACHINES},
                    "Water heating": "LPG water heating",
                }
            )
        )
        assert result == (139 + 689, 139)

    def test_it_returns_ngas_if_both_ngas_and_lpg(self):
        result = get_fixed_costs_per_year(
            pd.Series(
                {
                    **base_household,
                    **{x: 1 for x in NGAS_MACHINES},
                    **{x: 1 for x in LPG_MACHINES},
                    "Water heating": "LPG water heating",
                }
            )
        )
        assert result == (587 + 689, 587)


test_household = pd.Series(
    {
        **base_household,
        # 1 heat pump, 2 resistive, 1 biogas (not counted)
        "Home heating_Heat pump split system (an individual unit in a room(s))": 1,
        "Home heating_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 1,
        "Home heating_Other (please specify)": 1,
        "Home heating_Other (please specify)_0": "Biogas fireplace",
        "Home heating number_Heat pump split system (an individual unit in a room(s))": 1.0,
        "Home heating number_Electric resistance heater (e.g. electric bar, fan, oil, ceramic panel)": 2.0,
        "Water heating": "Solar water heating",
        "Cooktop_Electric resistance cooktop": 1.0,
    }
)


class TestGetHomeHeatingOpexSavings:
    def test_it_calculates_correctly_for_home_heating(self):
        opex, savings = get_home_heating_opex_savings(test_household)
        expected_opex = (2.7 / 2 * 0.242 * 365.25 * 15) + (
            2 * 9.3 / 8 * 0.242 * 365.25 * 15
        )
        assert opex == expected_opex

        # It would take 1.5 heat pumps to replace 1 heat pump + 2 resistive (the 1 biogas is not considered)
        expected_savings = opex - ((2.7 / 2 * 0.242 * 365.25 * 15) * (1 + 0.25 * 2))
        assert round(savings, 4) == round(expected_savings, 4)


class TestGetWaterHeatingOpexSavings:
    def test_it_calculates_correctly_for_solar_heating(self):
        opex, savings = get_water_heating_opex_savings("Solar water heating")
        assert opex == 2.07 * 0.242 * 365.25 * 15
        assert savings == 0

    def test_it_calculates_correctly_for_gas_heating(self):
        opex, savings = get_water_heating_opex_savings("Gas water heating")
        expected_opex = 6.88 * 0.11 * 365.25 * 15
        assert opex == expected_opex
        assert savings == expected_opex - (2.07 * 0.242 * 365.25 * 15)


class TestGetCooktopOpexSavings:
    cooktop_cols = list(COOKTOP_KWH_PER_DAY.keys())

    def test_it_calculates_correctly_for_resistive(self):
        opex, savings = get_cooktop_opex_savings(test_household[self.cooktop_cols])
        assert opex == 0.89 * 0.242 * 365.25 * 15
        assert savings == 0

    def test_it_calculates_correctly_for_gas(self):
        opex, savings = get_cooktop_opex_savings(
            pd.Series({**base_household, "Cooktop_Gas cooktop": 1})
        )
        expected_opex = 2.08 * 0.11 * 365.25 * 15
        assert opex == expected_opex
        assert savings == expected_opex - (0.81 * 0.242 * 365.25 * 15)


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
    petrol_opex = (32 * 0.27) * 365.25 * 15
    diesel_opex = (28.4 * 0.21) * 365.25 * 15
    ev_opex = (8.027 * 0.242) * 365.25 * 15
    plugin_opex = petrol_opex * 0.6 + ev_opex * 0.4
    hybrid_opex = petrol_opex * 0.7 + ev_opex * 0.3

    def test_it_returns_zeros_if_no_vehicle(self):
        assert get_vehicle_opex_savings(pd.Series(self.base)) == (0, 0)

    def test_it_returns_zeros_if_not_sure(self):
        assert get_vehicle_opex_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 1,
                    "Vehicles fuel/energy type_Vehicle 1": "I’m not sure",
                }
            )
        ) == (0, 0)

    def test_it_returns_opex_savings_for_one_petrol_vehicle(self):
        household = pd.Series(
            {
                **self.base,
                "Vehicles": 1,
                "Vehicles fuel/energy type_Vehicle 1": "Petrol",
                "Vehicles distance_Vehicle 1": "100-199km",
            }
        )
        distance_per_week = 150  # taking the middle of the 100-199km range
        distance_per_year = distance_per_week * 52
        pct_of_avg = distance_per_year / 11000
        opex_before = self.petrol_opex * pct_of_avg  # No RUCs

        rucs_after = 76 * distance_per_year / 1000
        opex_after = self.ev_opex * pct_of_avg + rucs_after

        opex, savings = get_vehicle_opex_savings(household)

        assert opex == opex_before
        assert savings == opex_before - opex_after

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
        opex_before = self.petrol_opex
        opex_after = self.ev_opex + 76 * 11000 / 1000
        opex, savings = get_vehicle_opex_savings(household)
        assert opex == opex_before
        assert savings == opex_before - opex_after

    def test_it_returns_opex_savings_for_multiple_ff_vehicles(self):
        opex, savings = get_vehicle_opex_savings(
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

        expected_opex = (
            (self.petrol_opex * 25 * 52 / 11000)
            + (self.petrol_opex * 150 * 52 / 11000)
            + (self.diesel_opex * 250 * 52 / 11000 + 76 * 250 * 52 / 1000)
        )
        assert opex == expected_opex

        expected_savings = expected_opex - (
            (self.ev_opex * 25 * 52 / 11000 + 76 * 25 * 52 / 1000)
            + (self.ev_opex * 150 * 52 / 11000 + 76 * 150 * 52 / 1000)
            + (self.ev_opex * 250 * 52 / 11000 + 76 * 250 * 52 / 1000)
        )
        assert savings == pytest.approx(expected_savings)

    def test_it_calculates_correctly_for_PHEV(self):
        opex, savings = get_vehicle_opex_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 1,
                    "Vehicles fuel/energy type_Vehicle 1": "Plug-in Hybrid",
                    "Vehicles distance_Vehicle 1": "0-50km",
                }
            )
        )
        expected_opex = self.plugin_opex * (25 * 52 / 11000) + (38 * 25 * 52 / 1000)
        assert opex == expected_opex
        assert savings == expected_opex - (
            self.ev_opex * (25 * 52 / 11000) + (76 * 25 * 52 / 1000)
        )

    def test_it_calculates_correctly_for_HEV(self):
        opex, savings = get_vehicle_opex_savings(
            pd.Series(
                {
                    **self.base,
                    "Vehicles": 1,
                    "Vehicles fuel/energy type_Vehicle 1": "Hybrid",
                    "Vehicles distance_Vehicle 1": "0-50km",
                }
            )
        )
        expected_opex = self.hybrid_opex * 25 / 11000 * 52  # no RUCs
        assert opex == expected_opex
        assert savings == expected_opex - (
            self.ev_opex * (25 / 11000 * 52) + (76 * 25 * 52 / 1000)
        )

    def test_it_does_not_switch_for_electric_vehicles(self):
        total_opex, total_savings = get_vehicle_opex_savings(
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
        expected_total_opex = (
            (self.petrol_opex * (25 * 52 / 11000))
            + (self.ev_opex * (150 * 52 / 11000) + (76 * 150 * 52 / 1000))
            + (self.plugin_opex * (250 * 52 / 11000) + (38 * 250 * 52 / 1000))
        )
        assert total_opex == expected_total_opex
        expected_total_savings = expected_total_opex - (
            (self.ev_opex * (25 * 52 / 11000) + (76 * 25 * 52 / 1000))
            + (self.ev_opex * (150 * 52 / 11000) + (76 * 150 * 52 / 1000))
            + (self.ev_opex * (250 * 52 / 11000) + (76 * 250 * 52 / 1000))
        )
        assert total_savings == pytest.approx(expected_total_savings)
