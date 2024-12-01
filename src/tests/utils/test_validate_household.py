import pytest

from unittest import TestCase
from unittest.mock import patch

from models.electrify_household import install_battery
from openapi_client.models import Household, Solar, Battery

from utils.validate_household import validate_household, ensure_no_battery_without_solar


class TestValidateHousehold(TestCase):

    @patch("utils.validate_household.ensure_no_battery_without_solar")
    def test_validate_household_calls_ensure_no_battery_without_solar(
        self, mock_ensure
    ):
        household = Household(
            solar=Solar(has_solar=True), battery=Battery(has_battery=True)
        )
        validate_household(household)
        mock_ensure.assert_called_once_with(household.solar, household.battery)


class TestEnsureNoBatteryWithoutSolar(TestCase):
    def test_it_passes_if_solar_no_battery(self):
        # Has no battery
        ensure_no_battery_without_solar(
            Solar(has_solar=True, size=10),
            Battery(has_battery=False),
        )
        # Has no battery and doesn't want to install one
        ensure_no_battery_without_solar(
            Solar(has_solar=True, size=10),
            Battery(has_battery=False, size=10, install_battery=False),
        )
        # Has no battery (+ wants solar)
        ensure_no_battery_without_solar(
            Solar(has_solar=False, size=10, install_solar=True),
            Battery(has_battery=False),
        )
        # Has no battery and doesn't want to install one (+ wants solar)
        ensure_no_battery_without_solar(
            Solar(has_solar=False, size=10, install_solar=True),
            Battery(has_battery=False, size=10, install_battery=False),
        )

    def test_it_passes_if_solar_and_battery(self):
        ensure_no_battery_without_solar(
            Solar(has_solar=True, size=10),
            Battery(has_battery=True, capacity=10),
        )
        ensure_no_battery_without_solar(
            Solar(has_solar=True, size=10),
            Battery(has_battery=False, capacity=10, install_battery=True),
        )
        ensure_no_battery_without_solar(
            Solar(has_solar=False, size=10, install_solar=True),
            Battery(has_battery=True, capacity=10),
        )
        ensure_no_battery_without_solar(
            Solar(has_solar=False, size=10, install_solar=True),
            Battery(has_battery=False, capacity=10, install_battery=True),
        )

    def test_it_passes_if_no_solar_no_battery(self):
        ensure_no_battery_without_solar(
            Solar(has_solar=False),
            Battery(has_battery=False),
        )
        ensure_no_battery_without_solar(
            Solar(has_solar=False),
            Battery(has_battery=False, capacity=10, install_battery=False),
        )
        ensure_no_battery_without_solar(
            Solar(has_solar=False, size=10, install_solar=False),
            Battery(has_battery=False),
        )
        ensure_no_battery_without_solar(
            Solar(has_solar=False, size=10, install_solar=False),
            Battery(has_battery=False, capacity=10, install_battery=False),
        )

    def test_it_fails_if_no_solar_but_has_battery(self):
        with pytest.raises(ValueError):
            ensure_no_battery_without_solar(
                Solar(has_solar=False),
                Battery(has_battery=True),
            )
        with pytest.raises(ValueError):
            ensure_no_battery_without_solar(
                Solar(has_solar=False),
                Battery(has_battery=False, capacity=10, install_battery=True),
            )
        with pytest.raises(ValueError):
            ensure_no_battery_without_solar(
                Solar(has_solar=False, size=10, install_solar=False),
                Battery(has_battery=True),
            )
        with pytest.raises(ValueError):
            ensure_no_battery_without_solar(
                Solar(has_solar=False, size=10, install_solar=False),
                Battery(has_battery=False, capacity=10, install_battery=True),
            )
