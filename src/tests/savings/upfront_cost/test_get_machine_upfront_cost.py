from unittest import TestCase
from openapi_client.models.cooktop_enum import CooktopEnum
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
        result = get_solar_upfront_cost(mock_household, mock_household_electrified)
        assert result == 1


class TestGetBatteryUpfrontCost(TestCase):
    def test_it_gets_battery_upfront_cost(self):
        result = get_battery_upfront_cost(mock_household, mock_household_electrified)
        assert result == 1


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
    def test_it_gets_space_heating_upfront_cost(self):
        result = get_space_heating_upfront_cost(
            SpaceHeatingEnum.GAS, SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
        )
        assert result == 1
