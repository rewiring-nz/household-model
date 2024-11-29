from constants.fuel_stats import FuelTypeEnum
import pytest
from constants.utils import DAYS_PER_YEAR, HOURS_PER_YEAR, PeriodEnum
from openapi_client.models.battery import Battery
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from params import OPERATIONAL_LIFETIME
from savings.energy.get_energy_consumption import (
    EnergyConsumption,
    get_e_generated_from_solar,
    get_e_consumed_from_solar,
    get_e_consumed_from_battery,
    get_energy_consumption,
)
from savings.energy.get_machine_energy import MachineEnergyNeeds


class TestGetEnergyConsumption:
    def test_large_solar_install_and_large_battery(self):
        energy_needs = MachineEnergyNeeds(
            appliances=2000,
            vehicles=4000,
            other_appliances=1000,
        )  # 7000 kWh total per year
        solar = Solar(has_solar=True, size=20)
        battery = Battery(has_battery=True, capacity=40)

        expected = EnergyConsumption(
            consumed_from_solar=3000,
            consumed_from_battery=11828.109900000001,
            consumed_from_grid=0,
            exported_to_grid=18294.11768,  # generated from solar (25294.11768) - total energy needs (7000)
        )
        result = get_energy_consumption(
            energy_needs,
            solar,
            battery,
            LocationEnum.AUCKLAND_CENTRAL,
            PeriodEnum.YEARLY,
        )

        assert result == expected


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


class TestGetEConsumedFromSolar:
    def test_calculates_consumption_when_below_generation(self):
        e_generated_from_solar = 10000.0
        e_needs = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 5000.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 3000.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
        }

        e_consumed_from_solar = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 2500.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 1500.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
        }
        e_remaining_from_solar = 10000 - (2500 + 1500)
        e_needs_remaining = {
            "appliances": {FuelTypeEnum.ELECTRICITY: 2500.0},
            "vehicles": {FuelTypeEnum.ELECTRICITY: 1500.0},
            "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
        }
        assert get_e_consumed_from_solar(e_generated_from_solar, e_needs) == (
            e_consumed_from_solar,
            e_remaining_from_solar,
            e_needs_remaining,
        )

    def test_caps_consumption_at_generation(self):
        assert get_e_consumed_from_solar(
            5000.0,
            # At 50% self-consumption, there's an extra 1000 kWh required that's not met by solar
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 8000.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 4000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        ) == (
            # consumed from solar
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 3500.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 1500.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
            # remaining from solar
            0,
            # remaining needs; assume even distribution
            {
                "appliances": {FuelTypeEnum.ELECTRICITY: 5500.0},
                "vehicles": {FuelTypeEnum.ELECTRICITY: 2500.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
        )

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
                "vehicles": {FuelTypeEnum.ELECTRICITY: 1000.0},
                "other_appliances": {FuelTypeEnum.ELECTRICITY: 0.0},
            },
            # remaining from solar
            4250,
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

    def test_period(self):
        capacity = 10
        expected_daily = 10 * 1 * 0.8522 * (1 - 0.05)
        assert (
            get_e_consumed_from_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100,
                e_consumed_from_solar=0,
                period=PeriodEnum.DAILY,
            )
            == expected_daily
        )
        assert (
            get_e_consumed_from_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100 * 7,
                e_consumed_from_solar=0,
                period=PeriodEnum.WEEKLY,
            )
            == expected_daily * 7
        )
        assert (
            get_e_consumed_from_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100 * 365.25,
                e_consumed_from_solar=0,
                period=PeriodEnum.YEARLY,
            )
            == expected_daily * DAYS_PER_YEAR
        )
        assert (
            get_e_consumed_from_battery(
                battery_capacity=capacity,
                e_generated_from_solar=100 * 365.25 * 30,
                e_consumed_from_solar=0,
                period=PeriodEnum.OPERATIONAL_LIFETIME,
            )
            == expected_daily * DAYS_PER_YEAR * OPERATIONAL_LIFETIME
        )
