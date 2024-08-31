from models.electrify_household import (
    electrify_cooktop,
    electrify_household,
    electrify_space_heating,
    electrify_vehicle,
    electrify_water_heating,
)
from openapi_client.models import CooktopEnum
from openapi_client.models.battery import Battery
from openapi_client.models.household import Household
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.solar import Solar
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.vehicle import Vehicle
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from tests.mocks import mock_household, mock_vehicle_diesel, mock_solar, mock_battery


class TestElectrifyHousehold:
    def test_it_electrifies_household_correctly(self):
        electrified = electrify_household(mock_household)
        assert electrified == Household(
            **{
                "location": LocationEnum.AUCKLAND_CENTRAL,
                "occupancy": 4,
                "space_heating": SpaceHeatingEnum.WOOD,
                "water_heating": WaterHeatingEnum.GAS,
                "cooktop": CooktopEnum.ELECTRIC_RESISTANCE,
                "vehicles": [
                    Vehicle(
                        fuel_type=VehicleFuelTypeEnum.ELECTRIC,
                        kms_per_week=250,
                        switch_to_ev=True,
                    ),
                    mock_vehicle_diesel,  # did not want to switch this one
                ],
                "solar": Solar(has_solar=True, size=7, install_solar=None),
                "battery": Battery(
                    has_battery=False, capacity=13, install_battery=False
                ),  # Did not want a battery
            }
        )


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


class TestElectrifyCooktop:
    def test_it_replaces_fossil_fuel_cooktops_with_heat_pump(self):
        assert electrify_cooktop(CooktopEnum.GAS) == CooktopEnum.ELECTRIC_INDUCTION
        assert electrify_cooktop(CooktopEnum.LPG) == CooktopEnum.ELECTRIC_INDUCTION
        assert electrify_cooktop(CooktopEnum.WOOD) == CooktopEnum.ELECTRIC_INDUCTION

    def test_no_change_if_resistive(self):
        assert (
            electrify_cooktop(CooktopEnum.ELECTRIC_RESISTANCE)
            == CooktopEnum.ELECTRIC_RESISTANCE
        )

    def test_no_change_if_already_induction(self):
        assert (
            electrify_cooktop(CooktopEnum.ELECTRIC_INDUCTION)
            == CooktopEnum.ELECTRIC_INDUCTION
        )


class TestElectrifyVehicle:
    mock_kms_per_week = 123
    ev = Vehicle(
        fuelType=VehicleFuelTypeEnum.ELECTRIC,
        kms_per_week=mock_kms_per_week,
        switchToEV=None,
    )

    def test_it_replaces_vehicle_with_ev_if_switch_to_ev_is_true(self):
        for fuel_type in VehicleFuelTypeEnum:
            assert (
                electrify_vehicle(
                    Vehicle(
                        fuelType=fuel_type.value,
                        kms_per_week=self.mock_kms_per_week,
                        switchToEV=True,
                    )
                )
                == self.ev
            )

    def test_it_does_not_replace_if_switch_to_ev_is_false(self):
        for fuel_type in VehicleFuelTypeEnum:
            vehicle = Vehicle(
                fuelType=fuel_type.value,
                kms_per_week=self.mock_kms_per_week,
                switchToEV=False,
            )
            assert electrify_vehicle(vehicle) == vehicle

    def test_no_change_if_already_ev(self):
        assert electrify_vehicle(self.ev) == self.ev
