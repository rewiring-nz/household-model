from unittest.mock import MagicMock, patch

from models.electrify_household import (
    electrify_cooktop,
    electrify_household,
    install_battery,
    install_solar,
    electrify_space_heating,
    electrify_vehicle,
    electrify_water_heating,
    should_electrify,
    should_install,
)
from openapi_client.models import (
    Battery,
    CooktopEnum,
    Solar,
    SpaceHeatingEnum,
    Vehicle,
    VehicleFuelTypeEnum,
    WaterHeatingEnum,
)
from tests.mocks import mock_household, mock_household_electrified


class TestElectrifyHousehold:
    def test_it_electrifies_household_correctly(self):
        electrified = electrify_household(mock_household)
        assert electrified == mock_household_electrified


class TestShouldElectrify:
    mock_electrify_func = MagicMock()
    mock_electrify_func.return_value = SpaceHeatingEnum.ELECTRIC_HEAT_PUMP

    def test_it_calls_electrify_func_correctly(self):
        should_electrify(SpaceHeatingEnum.GAS, self.mock_electrify_func)
        self.mock_electrify_func.assert_called_once_with(SpaceHeatingEnum.GAS)

    def test_it_returns_true_if_current_and_func_output_are_different(self):
        assert should_electrify(SpaceHeatingEnum.GAS, self.mock_electrify_func)

    def test_it_returns_true_if_current_and_func_output_are_same(self):
        assert not should_electrify(
            SpaceHeatingEnum.ELECTRIC_HEAT_PUMP, self.mock_electrify_func
        )


class TestShouldInstall:
    def test_it_returns_true_if_no_solar_and_wants_solar(self):
        assert should_install(Solar(has_solar=False, size=7, install_solar=True))

    def test_it_returns_false_if_no_solar_and_does_not_want_solar(self):
        assert not should_install(Solar(has_solar=False, size=7, install_solar=False))

    def test_it_returns_false_if_has_solar(self):
        assert not should_install(Solar(has_solar=True, size=7))
        assert not should_install(Solar(has_solar=True, size=7, install_solar=None))

    def test_it_returns_true_if_no_battery_and_wants_battery(self):
        assert should_install(Battery(has_battery=False, size=7, install_battery=True))

    def test_it_returns_false_if_no_battery_and_does_not_want_battery(self):
        assert not should_install(
            Battery(has_battery=False, size=7, install_battery=False)
        )

    def test_it_returns_false_if_has_battery(self):
        assert not should_install(Battery(has_battery=True, size=7))
        assert not should_install(
            Battery(has_battery=True, size=7, install_battery=None)
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


@patch("models.electrify_household.should_install")
class TestInstallSolar:
    def test_it_installs_solar_if_should_install(self, mock_should_install):
        mock_should_install.side_effect = [True]
        assert install_solar(
            Solar(has_solar=False, size=7, install_solar=True)
        ) == Solar(has_solar=True, size=7, install_solar=None)

    def test_it_does_nothing_if_should_not_install(self, mock_should_install):
        mock_should_install.side_effect = [False, False, False]
        assert install_solar(
            Solar(has_solar=False, size=7, install_solar=False)
        ) == Solar(has_solar=False, size=7, install_solar=False)

        assert install_solar(
            Solar(has_solar=True, size=7, install_solar=None)
        ) == Solar(has_solar=True, size=7, install_solar=None)

        assert install_solar(Solar(has_solar=True, size=7)) == Solar(
            has_solar=True, size=7
        )


@patch("models.electrify_household.should_install")
class TestInstallBattery:
    def test_it_installs_battery_if_should_install(self, mock_should_install):
        mock_should_install.side_effect = [True]
        assert install_battery(
            Battery(has_battery=False, size=7, install_battery=True)
        ) == Battery(has_battery=True, size=7, install_battery=None)

    def test_it_does_nothing_if_should_not_install(self, mock_should_install):
        mock_should_install.side_effect = [False, False, False]
        assert install_battery(
            Battery(has_battery=False, size=7, install_battery=False)
        ) == Battery(has_battery=False, size=7, install_battery=False)

        assert install_battery(
            Battery(has_battery=True, size=7, install_battery=None)
        ) == Battery(has_battery=True, size=7, install_battery=None)

        assert install_battery(Battery(has_battery=True, size=7)) == Battery(
            has_battery=True, size=7
        )
