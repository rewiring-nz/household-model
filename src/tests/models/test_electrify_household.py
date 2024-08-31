from models.electrify_household import (
    electrify_household,
    electrify_space_heating,
    electrify_water_heating,
)
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from tests.mocks import mock_household


class TestElectrifySpaceHeating:
    def test_it_replaces_non_electric_space_heaters_with_heat_pump(self):
        assert (
            electrify_space_heating(SpaceHeatingEnum.WOOD)
            == SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
        )
        assert (
            electrify_space_heating(SpaceHeatingEnum.GAS)
            == SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
        )
        assert (
            electrify_space_heating(SpaceHeatingEnum.LPG)
            == SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
        )

    def test_it_replaces_resistive_heater_with_heat_pump(self):
        assert (
            electrify_space_heating(SpaceHeatingEnum.ELECTRIC_RESISTANCE)
            == SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
        )

    def test_no_change_if_already_heat_pump(self):
        assert (
            electrify_space_heating(SpaceHeatingEnum.ELECTRIC_HEAT_PUMP)
            == SpaceHeatingEnum.ELECTRIC_HEAT_PUMP
        )


class TestElectrifyWaterHeating:
    def test_it_replaces_fossil_fuel_water_heaters_with_heat_pump(self):
        assert (
            electrify_water_heating(WaterHeatingEnum.GAS)
            == WaterHeatingEnum.ELECTRIC_HEAT_PUMP
        )
        assert (
            electrify_water_heating(WaterHeatingEnum.LPG)
            == WaterHeatingEnum.ELECTRIC_HEAT_PUMP
        )

    def test_no_change_if_resistive_or_solar(self):
        assert (
            electrify_water_heating(WaterHeatingEnum.ELECTRIC_RESISTANCE)
            == WaterHeatingEnum.ELECTRIC_RESISTANCE
        )
        assert electrify_water_heating(WaterHeatingEnum.SOLAR) == WaterHeatingEnum.SOLAR

    def test_no_change_if_already_heat_pump(self):
        assert (
            electrify_water_heating(WaterHeatingEnum.ELECTRIC_HEAT_PUMP)
            == WaterHeatingEnum.ELECTRIC_HEAT_PUMP
        )
