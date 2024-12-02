from unittest.mock import patch
from constants.fuel_stats import FuelTypeEnum
import pytest
from constants.utils import DAYS_PER_YEAR, HOURS_PER_YEAR, PeriodEnum
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from params import OPERATIONAL_LIFETIME
from savings.energy.get_electricity_consumption import (
    get_e_generated_from_solar,
    get_e_consumed_from_solar,
    get_e_stored_in_battery,
    _get_max_e_consumed_from_solar,
    sum_energy_for_fuel_type,
)


class TestSumEnergyForFuelType:
    def test_basic_electricity_summation(self):
        e_needs = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 5000.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 3000.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 14.0},
        }

        result = sum_energy_for_fuel_type(e_needs, FuelTypeEnum.ELECTRICITY)
        assert result == 5000.0 + 3000.0 + 14.0

    def test_multiple_fuel_types_in_category(self):
        e_needs = {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 5000.0,
                FuelTypeEnum.NATURAL_GAS: 2000.0,
            },
            "vehicles": {FuelTypeEnum.ELECTRICITY: 3000.0, FuelTypeEnum.PETROL: 1000.0},
        }
        result = sum_energy_for_fuel_type(e_needs, FuelTypeEnum.ELECTRICITY)
        assert result == (5000.0 + 3000.0)

    def test_missing_category(self):
        e_needs = {
            "vehicles": {FuelTypeEnum.ELECTRICITY: 3000.0},
        }

        result = sum_energy_for_fuel_type(e_needs, FuelTypeEnum.ELECTRICITY)
        assert result == (3000.0)

    def test_no_matching_fuel_type(self):
        e_needs = {
            "appliances": {FuelTypeEnum.NATURAL_GAS: 5000.0},
            "vehicles": {FuelTypeEnum.PETROL: 3000.0},
        }
        result = sum_energy_for_fuel_type(e_needs, FuelTypeEnum.ELECTRICITY)
        assert result == 0

    def test_empty_needs(self):
        e_needs = {}
        result = sum_energy_for_fuel_type(e_needs, FuelTypeEnum.ELECTRICITY)
        assert result == 0


class TestGetEGeneratedFromSolar:
    def test_calculates_generation_correctly_for_sydney(self):
        solar = Solar(has_solar=True, size=6.6)
        expected_generation = solar.size * 0.155 * 8766 * 0.9308

        result = get_e_generated_from_solar(solar, LocationEnum.AUCKLAND_CENTRAL)

        assert result == expected_generation

    def test_different_locations_give_different_results(self):
        solar = Solar(has_solar=True, size=5.0)
        assert get_e_generated_from_solar(
            solar, LocationEnum.AUCKLAND_CENTRAL
        ) > get_e_generated_from_solar(solar, LocationEnum.SOUTHLAND)

    def test_zero_solar_size_returns_zero(self):
        assert (
            get_e_generated_from_solar(
                Solar(has_solar=True, size=0), LocationEnum.AUCKLAND_CENTRAL
            )
            == 0.0
        )

    def test_no_solar_returns_zero(self):
        assert (
            get_e_generated_from_solar(
                Solar(has_solar=False, size=9), LocationEnum.AUCKLAND_CENTRAL
            )
            == 0.0
        )

    def test_install_solar_none_returns_zero(self):
        assert (
            get_e_generated_from_solar(
                Solar(hasSolar=True, size=6.6, install_solar=None),
                LocationEnum.AUCKLAND_CENTRAL,
            )
            == 6.6 * 0.155 * 8766 * 0.9308
        )

    def test_larger_system_generates_proportionally_more(self):
        small_size = Solar(has_solar=True, size=5.0)
        large_size = Solar(has_solar=True, size=10.0)
        location = LocationEnum.OTAGO

        small_generation = get_e_generated_from_solar(small_size, location)
        large_generation = get_e_generated_from_solar(large_size, location)

        assert large_generation == 2 * small_generation

    def test_period(self):
        solar = Solar(has_solar=True, size=5.0)
        location = LocationEnum.AUCKLAND_CENTRAL

        assert (
            get_e_generated_from_solar(solar, location, PeriodEnum.DAILY)
            == 5 * 0.155 * 0.9308 * 24
        )
        assert (
            get_e_generated_from_solar(solar, location, PeriodEnum.WEEKLY)
            == 5 * 0.155 * 0.9308 * 24 * 7
        )
        assert (
            get_e_generated_from_solar(solar, location, PeriodEnum.YEARLY)
            == 5 * 0.155 * 0.9308 * HOURS_PER_YEAR
        )
        assert (
            get_e_generated_from_solar(solar, location, PeriodEnum.OPERATIONAL_LIFETIME)
            == 5 * 0.155 * 0.9308 * HOURS_PER_YEAR * OPERATIONAL_LIFETIME
        )


class TestGetMaxEConsumedFromSolar:
    def test_it_uses_self_consumption_correctly(self):
        e_needs = {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 5000.0,
                FuelTypeEnum.NATURAL_GAS: 2000.0,
            },
            "vehicles": {
                FuelTypeEnum.ELECTRICITY: 3000.0,
                FuelTypeEnum.PETROL: 6000.0,
                FuelTypeEnum.DIESEL: 2500.0,
            },
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 14.0},
        }
        assert _get_max_e_consumed_from_solar(
            e_needs,
        ) == {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 2500,
            },
            "vehicles": {
                FuelTypeEnum.ELECTRICITY: 1500,
            },
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 7},
        }

    def test_it_handles_missing_categories(self):
        e_needs = {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 5000.0,
                FuelTypeEnum.NATURAL_GAS: 2000.0,
            },
        }
        assert _get_max_e_consumed_from_solar(e_needs) == {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 2500.0,
            },
            # Doesn't fill in missing categories
        }

    def test_it_handles_no_electricity_fuel_type(self):
        e_needs = {
            "appliances": {
                FuelTypeEnum.NATURAL_GAS: 2000.0,
            },
            "vehicles": {
                FuelTypeEnum.DIESEL: 2000.0,
            },
        }
        assert _get_max_e_consumed_from_solar(e_needs) == {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 0,
            },
            "vehicles": {
                FuelTypeEnum.ELECTRICITY: 0,
            },
        }


class TestGetEConsumedFromSolar:
    def test_calculates_consumption_when_below_generation(self):
        e_generated_from_solar = 10000.0
        e_needs = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 5000.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 3000.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 14.0},
        }

        result = get_e_consumed_from_solar(e_generated_from_solar, e_needs)

        e_consumed_from_solar = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 2500.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 1500.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 7.0},
        }
        e_remaining_from_solar = 10000.0 - (2500 + 1500 + 7)
        e_needs_remaining = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 2500.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 1500.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 7.0},
        }
        assert result == (
            e_consumed_from_solar,
            e_remaining_from_solar,
            e_needs_remaining,
        )

    def test_ignores_non_electric_needs(self):
        e_generated_from_solar = 10000.0
        e_needs = {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 5000.0,
                FuelTypeEnum.NATURAL_GAS: 2000.0,
            },
            "vehicles": {
                FuelTypeEnum.ELECTRICITY: 3000.0,
                FuelTypeEnum.PETROL: 6000.0,
                FuelTypeEnum.DIESEL: 2500.0,
            },
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 14.0},
        }

        e_consumed_from_solar = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 2500.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 1500.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 7.0},
        }
        e_remaining_from_solar = 10000 - (2500 + 1500 + 7)
        e_needs_remaining = {
            "appliances": {
                FuelTypeEnum.ELECTRICITY: 2500.0,
                FuelTypeEnum.NATURAL_GAS: 2000.0,
            },
            "vehicles": {
                FuelTypeEnum.ELECTRICITY: 1500.0,
                FuelTypeEnum.PETROL: 6000.0,
                FuelTypeEnum.DIESEL: 2500.0,
            },
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 7.0},
        }
        assert get_e_consumed_from_solar(e_generated_from_solar, e_needs) == (
            e_consumed_from_solar,
            e_remaining_from_solar,
            e_needs_remaining,
        )

    def test_caps_consumption_at_generation(self):
        result = get_e_consumed_from_solar(
            5000.0,
            # At 50% self-consumption, there's an extra 1000 kWh required that's not met by solar
            # This should be distributed proportionally to the self-consumed values
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 8000.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 4000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        )
        expected = (
            # consumed from solar
            {
                "appliances": {
                    FuelTypeEnum.ELECTRICITY: (8000 * 0.5) - (1000 * 4000 / 6000)
                },
                "vehicles": {
                    FuelTypeEnum.ELECTRICITY: (4000 * 0.5) - (1000 * 2000 / 6000)
                },
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
            # remaining from solar
            0,
            # remaining needs; assume even distribution
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 4666.666666666666},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 2333.333333333333},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        )
        assert result == expected

    def test_all_electric_needs_met(self):
        with patch(
            "savings.energy.get_electricity_consumption.MACHINE_CATEGORY_TO_SELF_CONSUMPTION_RATE",
            {
                "appliances": 1,  # 100% self-consumption
                "vehicles": 1,
                "other_appliances": 1,
            },
        ):
            result = get_e_consumed_from_solar(
                5000.0,
                {
                    # 4999 kWh required at 100% self-consumption for all categories
                    "appliances": {FuelTypeEnum.ELECTRICITY: 2000.0},
                    "vehicles": {FuelTypeEnum.ELECTRICITY: 2000.0},
                    "other_appliances": {FuelTypeEnum.ELECTRICITY: 999.0},
                },
            )
            expected = (
                # consumed from solar
                {
                    "appliances": {FuelTypeEnum.ELECTRICITY: 2000.0},
                    "vehicles": {FuelTypeEnum.ELECTRICITY: 2000.0},
                    "other_appliances": {FuelTypeEnum.ELECTRICITY: 999.0},
                },
                # remaining from solar
                1,
                # remaining needs - none
                {
                    "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                    "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                    "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                },
            )
        assert result == expected

    def test_no_generation(self):
        result = get_e_consumed_from_solar(
            0,
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 2000.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 2000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 999.0},
            },
        )
        expected = (
            # consumed from solar
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0},
            },
            # remaining from solar
            0,
            # remaining needs - none
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 2000.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 2000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 999.0},
            },
        )
        assert result == expected

    def test_with_only_appliance_load(self):
        assert get_e_consumed_from_solar(
            5000.0,
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 1500.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        ) == (
            # consumed from solar
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 750.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
            # remaining from solar
            4250.0,
            # remaining needs
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 750.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        )

    def test_with_only_vehicle_load(self):
        assert get_e_consumed_from_solar(
            5000.0,
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 2000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        ) == (
            # consumed from solar
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 1000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
            # remaining from solar
            4000,
            # remaining needs
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 1000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        )

    def test_with_only_other_appliances_load(self):
        assert get_e_consumed_from_solar(
            10.0,
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 14.0},
            },
        ) == (
            # consumed from solar
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 7.0},
            },
            # remaining from solar
            3,
            # remaining needs; assume even distribution
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 0.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 7.0},
            },
        )


class TestGetEnergyFromBattery:
    def test_when_remaining_energy_less_than_capacity_returns_remaining_energy(self):
        result = get_e_stored_in_battery(
            battery_capacity=10, e_generated_from_solar=100, e_consumed_from_solar=95
        )
        assert result == 5.0  # 100 - 95 = 5 kWh remaining

    def test_when_remaining_energy_exceeds_capacity_returns_capacity(self):
        # 3000 kWh/yr remaining from solar generation after self-consumption
        result = get_e_stored_in_battery(
            battery_capacity=10, e_generated_from_solar=3500, e_consumed_from_solar=500
        )
        # Battery capacity is 10 kWh/cycle, which is around 2957 kWh/yr
        battery_capacity_per_yr = 10 * 1 * 0.8522 * (1 - 0.05) * 365.25
        assert result == battery_capacity_per_yr

    def test_with_zero_battery_capacity_returns_zero(self):
        result = get_e_stored_in_battery(
            battery_capacity=0, e_generated_from_solar=100, e_consumed_from_solar=90
        )
        assert result == 0.0

    def test_with_equal_generation_and_consumption_returns_zero(self):
        result = get_e_stored_in_battery(
            battery_capacity=10, e_generated_from_solar=100, e_consumed_from_solar=100
        )
        assert result == 0.0

    def test_it_raises_error_if_more_consumed_than_generated(self):
        with pytest.raises(ValueError):
            get_e_stored_in_battery(10, 90, 100)

    def test_period(self):
        capacity = 10
        expected_daily = 10 * 1 * 0.8522 * (1 - 0.05)
        assert (
            get_e_stored_in_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100,
                e_consumed_from_solar=0,
                period=PeriodEnum.DAILY,
            )
            == expected_daily
        )
        assert (
            get_e_stored_in_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100 * 7,
                e_consumed_from_solar=0,
                period=PeriodEnum.WEEKLY,
            )
            == expected_daily * 7
        )
        assert (
            get_e_stored_in_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100 * 365.25,
                e_consumed_from_solar=0,
                period=PeriodEnum.YEARLY,
            )
            == expected_daily * DAYS_PER_YEAR
        )
        assert (
            get_e_stored_in_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100 * 365.25 * 30,
                e_consumed_from_solar=0,
                period=PeriodEnum.OPERATIONAL_LIFETIME,
            )
            == expected_daily * DAYS_PER_YEAR * OPERATIONAL_LIFETIME
        )
