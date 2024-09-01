from unittest import TestCase
from openapi_client.models.battery import Battery
from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from tests.mocks import mock_household, mock_household_electrified
from savings.upfront_cost.get_machine_upfront_cost import (
    get_battery_upfront_cost,
    get_cooktop_upfront_cost,
    get_solar_upfront_cost,
    get_space_heating_upfront_cost,
    get_water_heating_upfront_cost,
)


class TestGetSolarUpfrontCost(TestCase):
    def test_it_gets_solar_upfront_cost(self):
        wants_solar = Solar(has_solar=False, size=5, install_solar=True)
        assert get_solar_upfront_cost(wants_solar) == round(20500 / 9 * 5, 2)

    def test_it_returns_zero_if_already_has_solar(self):
        already_has_solar = Solar(has_solar=True, size=5, install_solar=None)
        assert get_solar_upfront_cost(already_has_solar) == 0

    def test_it_returns_zero_if_does_not_have_solar_and_does_not_want_it(self):
        no_solar = Solar(has_solar=False, size=5, install_solar=False)
        assert get_solar_upfront_cost(no_solar) == 0


class TestGetBatteryUpfrontCost(TestCase):
    def test_it_gets_battery_upfront_cost(self):
        wants_battery = Battery(has_battery=False, capacity=5, install_battery=True)
        assert get_battery_upfront_cost(wants_battery) == 1000 * 5

    def test_it_returns_zero_if_already_has_battery(self):
        already_has_battery = Battery(
            has_battery=True, capacity=5, install_battery=None
        )
        assert get_battery_upfront_cost(already_has_battery) == 0

    def test_it_returns_zero_if_does_not_have_battery_and_does_not_want_it(self):
        no_battery = Battery(has_battery=False, capacity=5, install_battery=False)
        assert get_battery_upfront_cost(no_battery) == 0


class TestGetCooktopUpfrontCost(TestCase):
    def test_it_returns_cooktop_upfront_cost_of_electrified_option_if_not_already_installed(
        self,
    ):
        switch_from_options = [CooktopEnum.GAS, CooktopEnum.LPG]
        for switch_from in switch_from_options:
            result = get_cooktop_upfront_cost(
                switch_from, CooktopEnum.ELECTRIC_INDUCTION
            )
            assert result == 1430 + 1265

        for switch_from in switch_from_options:
            result = get_cooktop_upfront_cost(
                switch_from, CooktopEnum.ELECTRIC_RESISTANCE
            )
            assert result == 879 + 288

    def test_it_returns_zero_if_electrified_option_already_installed(
        self,
    ):
        assert (
            get_cooktop_upfront_cost(
                CooktopEnum.ELECTRIC_INDUCTION, CooktopEnum.ELECTRIC_INDUCTION
            )
            == 0
        )
        assert (
            get_cooktop_upfront_cost(
                CooktopEnum.ELECTRIC_RESISTANCE,
                CooktopEnum.ELECTRIC_RESISTANCE,
            )
            == 0
        )

    def test_it_returns_zero_if_dont_know(
        self,
    ):
        assert (
            get_cooktop_upfront_cost(
                CooktopEnum.DONT_KNOW, CooktopEnum.ELECTRIC_INDUCTION
            )
            == 0
        )


class TestGetWaterHeatingUpfrontCost(TestCase):
    def test_it_returns_water_heating_upfront_cost_of_electrified_option_if_not_already_installed(
        self,
    ):
        switch_from_options = [WaterHeatingEnum.GAS, WaterHeatingEnum.LPG]
        for switch_from in switch_from_options:
            result = get_water_heating_upfront_cost(
                switch_from, WaterHeatingEnum.ELECTRIC_HEAT_PUMP
            )
            assert result == 4678 + 2321  # upfront cost of heat pump

        for switch_from in switch_from_options:
            result = get_water_heating_upfront_cost(
                switch_from, WaterHeatingEnum.ELECTRIC_RESISTANCE
            )
            assert result == 1975 + 1995  # upfront cost of electric resistance

    def test_it_returns_zero_if_electrified_option_already_installed(
        self,
    ):
        assert (
            get_water_heating_upfront_cost(
                WaterHeatingEnum.ELECTRIC_HEAT_PUMP, WaterHeatingEnum.ELECTRIC_HEAT_PUMP
            )
            == 0
        )
        assert (
            get_water_heating_upfront_cost(
                WaterHeatingEnum.ELECTRIC_RESISTANCE,
                WaterHeatingEnum.ELECTRIC_RESISTANCE,
            )
            == 0
        )

    def test_it_returns_zero_if_dont_know(
        self,
    ):
        assert (
            get_water_heating_upfront_cost(
                WaterHeatingEnum.DONT_KNOW, WaterHeatingEnum.ELECTRIC_HEAT_PUMP
            )
            == 0
        )


class TestGetSpaceHeatingUpfrontCost(TestCase):
    def test_it_returns_space_heating_upfront_cost_of_electrified_option_if_not_already_installed(
        self,
    ):
        for switch_from in [
            SpaceHeatingEnum.GAS,
            SpaceHeatingEnum.LPG,
            SpaceHeatingEnum.WOOD,
            SpaceHeatingEnum.ELECTRIC_RESISTANCE,
        ]:
            result = get_space_heating_upfront_cost(
                switch_from, SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
            )
            assert (
                result == (2728 + 1050) * 2
            )  # upfront cost of heat pump * 2 for average home

    def test_it_calibrates_number_of_space_heaters_according_to_location(
        self,
    ):
        assert (
            get_space_heating_upfront_cost(
                SpaceHeatingEnum.GAS,
                SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                LocationEnum.AUCKLAND_CENTRAL,
            )
            == (2728 + 1050) * 1
        )
        assert (
            get_space_heating_upfront_cost(
                SpaceHeatingEnum.GAS,
                SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                LocationEnum.CANTERBURY,
            )
            == (2728 + 1050) * 2
        )
        assert (
            get_space_heating_upfront_cost(
                SpaceHeatingEnum.GAS,
                SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                LocationEnum.WELLINGTON,
            )
            == (2728 + 1050) * 3
        )
        assert (
            get_space_heating_upfront_cost(
                SpaceHeatingEnum.GAS,
                SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                LocationEnum.OTAGO,
            )
            == (2728 + 1050) * 3
        )

    def test_it_returns_zero_if_electrified_option_already_installed(
        self,
    ):
        assert (
            get_space_heating_upfront_cost(
                SpaceHeatingEnum.ELECTRIC_HEAT_PUMP, SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
            )
            == 0
        )

    def test_it_returns_zero_if_dont_know(
        self,
    ):
        assert (
            get_space_heating_upfront_cost(
                SpaceHeatingEnum.DONT_KNOW, SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
            )
            == 0
        )
