import pytest
from constants.solar import SOLAR_OPERATIONAL_LIFETIME_YRS
from constants.utils import DAYS_PER_YEAR, HOURS_PER_YEAR, PeriodEnum
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from savings.opex.get_energy_consumption import (
    get_e_generated_from_solar,
    get_e_consumed_from_solar,
    get_e_consumed_from_battery,
)


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
                Solar(has_solar=False), LocationEnum.AUCKLAND_CENTRAL
            )
            == 0.0
        )

    def test_dont_install_solar_returns_zero(self):
        assert (
            get_e_generated_from_solar(
                Solar(has_solar=False, install_solar=False),
                LocationEnum.AUCKLAND_CENTRAL,
            )
            == 0.0
        )

    def test_install_solar_returns_val(self):
        solar = Solar(has_solar=False, install_solar=True, size=6.6)
        expected = solar.size * 0.155 * 8766 * 0.9308
        assert (
            get_e_generated_from_solar(
                solar,
                LocationEnum.AUCKLAND_CENTRAL,
            )
            == expected
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
            == 5 * 0.155 * 0.9308 * HOURS_PER_YEAR * SOLAR_OPERATIONAL_LIFETIME_YRS
        )


class TestGetEConsumedFromSolar:
    def test_calculates_consumption_when_below_generation(self):
        assert get_e_consumed_from_solar(10000.0, 5000.0, 3000.0) == 2500 + 1500

    def test_caps_consumption_at_generation(self):
        assert get_e_consumed_from_solar(5000.0, 6000.0, 6000.0) == 5000

    def test_with_zero_appliance_load(self):
        assert get_e_consumed_from_solar(5000.0, 0.0, 2000.0) == 1000

    def test_with_zero_vehicle_load(self):
        assert get_e_consumed_from_solar(5000.0, 3000.0, 0.0) == 1500

    def test_with_all_zeros(self):
        assert get_e_consumed_from_solar(0.0, 0.0, 0.0) == 0


class TestGetEnergyFromBattery:
    def test_when_remaining_energy_less_than_capacity_returns_remaining_energy(self):
        result = get_e_consumed_from_battery(
            battery_capacity=10, e_generated_from_solar=100, e_consumed_from_solar=95
        )
        assert result == 5.0  # 100 - 95 = 5 kWh remaining

    def test_when_remaining_energy_exceeds_capacity_returns_capacity(self):
        # 3000 kWh/yr remaining from solar generation after self-consumption
        result = get_e_consumed_from_battery(
            battery_capacity=10, e_generated_from_solar=3500, e_consumed_from_solar=500
        )
        # Battery capacity is 10 kWh/cycle, which is around 2957 kWh/yr
        battery_capacity_per_yr = 10 * 1 * 0.8522 * (1 - 0.05) * 365.25
        assert result == battery_capacity_per_yr

    def test_with_zero_battery_capacity_returns_zero(self):
        result = get_e_consumed_from_battery(
            battery_capacity=0, e_generated_from_solar=100, e_consumed_from_solar=90
        )
        assert result == 0.0

    def test_with_equal_generation_and_consumption_returns_zero(self):
        result = get_e_consumed_from_battery(
            battery_capacity=10, e_generated_from_solar=100, e_consumed_from_solar=100
        )
        assert result == 0.0

    def test_it_raises_error_if_more_consumed_than_generated(self):
        with pytest.raises(ValueError):
            get_e_consumed_from_battery(10, 90, 100)
