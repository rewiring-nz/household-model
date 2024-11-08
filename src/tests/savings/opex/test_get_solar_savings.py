import pytest
from savings.opex.get_solar_savings import get_energy_from_battery


class TestGetEnergyFromBattery:
    def test_when_remaining_energy_less_than_capacity_returns_remaining_energy(self):
        result = get_energy_from_battery(
            battery_capacity=10, e_generated_from_solar=100, e_consumed_from_solar=95
        )
        assert result == 5.0  # 100 - 95 = 5 kWh remaining

    def test_when_remaining_energy_exceeds_capacity_returns_capacity(self):
        # 3000 kWh/yr remaining from solar generation after self-consumption
        result = get_energy_from_battery(
            battery_capacity=10, e_generated_from_solar=3500, e_consumed_from_solar=500
        )
        # Battery capacity is 10 kWh/cycle, which is around 2957 kWh/yr
        battery_capacity_per_yr = 10 * 1 * 0.8522 * (1 - 0.05) * 365.25
        assert result == battery_capacity_per_yr

    def test_with_zero_battery_capacity_returns_zero(self):
        result = get_energy_from_battery(
            battery_capacity=0, e_generated_from_solar=100, e_consumed_from_solar=90
        )
        assert result == 0.0

    def test_with_equal_generation_and_consumption_returns_zero(self):
        result = get_energy_from_battery(
            battery_capacity=10, e_generated_from_solar=100, e_consumed_from_solar=100
        )
        assert result == 0.0

    def test_it_raises_error_if_more_consumed_than_generated(self):
        with pytest.raises(ValueError):
            get_energy_from_battery(10, 90, 100)
