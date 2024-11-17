import pytest

from unittest import TestCase
from unittest.mock import patch

from openapi_client.models import (
    SpaceHeatingEnum,
    CooktopEnum,
)

from constants.fuel_stats import (
    COST_PER_FUEL_KWH_TODAY,
    FuelTypeEnum,
)
from constants.machines.machine_info import MachineInfoMap
from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.space_heating import SPACE_HEATING_INFO
from constants.utils import PeriodEnum
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum
from savings.opex.get_machine_opex import (
    get_energy_per_period,
    get_energy_per_day,
    get_machine_opex_per_period,
    get_other_appliances_energy_per_period,
    get_other_appliances_opex,
    get_vehicle_opex,
    _get_hybrid_opex_per_day,
)
from tests.mocks import (
    mock_household,
    mock_vehicle_petrol,
    mock_vehicle_diesel,
    mock_vehicle_ev,
    mock_vehicle_hev,
    mock_vehicle_phev,
)

mock_energy_daily = 2.5
mock_energy_weekly = 17.5  # 12.345 * 7

mock_opex_daily = 12.345
mock_opex_weekly = 86.415  # 12.345 * 7


class TestGetEnergyPerDay(TestCase):
    mock_appliance_info: MachineInfoMap = {
        CooktopEnum.GAS: {"kwh_per_day": 10.0, "fuel_type": FuelTypeEnum.NATURAL_GAS},
        SpaceHeatingEnum.ELECTRIC_HEAT_PUMP: {
            "kwh_per_day": 5.0,
            "fuel_type": FuelTypeEnum.ELECTRICITY,
        },
    }

    def test_get_energy_per_day(self):
        assert get_energy_per_day(CooktopEnum.GAS, self.mock_appliance_info) == 10.0
        assert (
            get_energy_per_day(
                SpaceHeatingEnum.ELECTRIC_HEAT_PUMP, self.mock_appliance_info
            )
            == 5.0
        )

    def test_get_energy_per_day_handles_missing_kwh_per_day(self):
        mock_appliance_info = {
            CooktopEnum.GAS: {
                "kwh_per_day": None,
                "fuel_type": FuelTypeEnum.NATURAL_GAS,
            }
        }
        with self.assertRaises(ValueError):
            get_energy_per_day(CooktopEnum.GAS, mock_appliance_info)

    def test_get_energy_per_day_handles_invalid_machine_type(self):
        invalid_machine_type = CooktopEnum.GAS
        invalid_mock_appliance_info = {}
        with self.assertRaises(KeyError):
            get_energy_per_day(invalid_machine_type, invalid_mock_appliance_info)


@patch(
    "savings.opex.get_machine_opex.scale_daily_to_period",
    return_value=mock_energy_weekly,
)
@patch(
    "savings.opex.get_machine_opex.get_energy_per_day",
    return_value=mock_energy_daily,
)
class TestGetEnergyPerPeriod:
    def test_it_calls_get_energy_per_day_correctly(self, mock_get_energy_per_day, _):
        get_energy_per_period(mock_household.space_heating, SPACE_HEATING_INFO)
        mock_get_energy_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO
        )

    def test_it_calls_scale_daily_to_period_correctly(
        self, _, mock_scale_daily_to_period
    ):
        get_energy_per_period(mock_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY)
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, _, mock_scale_daily_to_period
    ):
        get_energy_per_period(mock_household.cooktop, COOKTOP_INFO)
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily, PeriodEnum.DAILY
        )

    def test_it_returns_energy_per_period(self, _, __):
        result = get_energy_per_period(mock_household.space_heating, SPACE_HEATING_INFO)
        assert result == 17.5


@patch(
    "savings.opex.get_machine_opex.scale_daily_to_period",
    return_value=mock_opex_weekly,
)
@patch(
    "savings.opex.get_machine_opex.get_energy_per_day",
    return_value=mock_energy_daily,
)
class TestGetMachineOpexPerPeriod:
    def test_it_calls_get_energy_per_period_if_energy_per_day_is_none(
        self, mock_get_energy_per_day, _
    ):
        get_machine_opex_per_period(mock_household.space_heating, SPACE_HEATING_INFO)
        mock_get_energy_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO
        )

    def test_it_calls_scale_daily_to_period_correctly_with_provided_energy_value(
        self, _, mock_scale_daily_to_period
    ):
        get_machine_opex_per_period(
            mock_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY, 5
        )
        # Electric resistive cooktop has volume rate of $0.26175/kWh
        mock_scale_daily_to_period.assert_called_once_with(
            5 * 0.26175, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_calculated_energy_value(
        self, _, mock_scale_daily_to_period
    ):
        get_machine_opex_per_period(
            mock_household.cooktop,
            COOKTOP_INFO,
            PeriodEnum.WEEKLY,
        )
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily * 0.26175, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_provided_energy_value_and_default_period(
        self, _, mock_scale_daily_to_period
    ):
        get_machine_opex_per_period(
            mock_household.cooktop, COOKTOP_INFO, energy_per_day=5
        )
        # Electric resistive cooktop has volume rate of $0.26175/kWh
        mock_scale_daily_to_period.assert_called_once_with(
            5 * 0.26175, PeriodEnum.DAILY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_calculated_energy_value_and_default_period(
        self, _, mock_scale_daily_to_period
    ):
        get_machine_opex_per_period(
            mock_household.cooktop,
            COOKTOP_INFO,
        )
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily * 0.26175, PeriodEnum.DAILY
        )

    def test_it_returns_opex_per_period_rounded_to_2dp(self, _, __):
        result = get_machine_opex_per_period(
            mock_household.space_heating, SPACE_HEATING_INFO, energy_per_day=5
        )
        assert result == 86.42


@patch(
    "savings.opex.get_machine_opex.scale_daily_to_period",
    return_value=mock_energy_weekly,
)
class TestGetOtherAppliancesEnergyPerPeriod:
    energy = 0.34 + 4.05 + 2.85

    def test_it_calls_scale_daily_to_period_correctly(self, mock_scale_daily_to_period):
        get_other_appliances_energy_per_period(PeriodEnum.WEEKLY)
        mock_scale_daily_to_period.assert_called_once_with(
            self.energy, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, mock_scale_daily_to_period
    ):
        get_other_appliances_energy_per_period()
        mock_scale_daily_to_period.assert_called_once_with(
            self.energy, PeriodEnum.DAILY
        )

    def test_it_returns_energy_per_period(self, _):
        assert get_other_appliances_energy_per_period(PeriodEnum.WEEKLY) == 17.5
        assert get_other_appliances_energy_per_period() == 17.5


@patch(
    "savings.opex.get_machine_opex.scale_daily_to_period",
    return_value=mock_opex_weekly,
)
class TestGetOtherAppliancesOpex:
    opex_daily = (0.34 + 4.05 + 2.85) * 0.26175

    def test_it_calls_scale_daily_to_period_correctly(self, mock_scale_daily_to_period):
        get_other_appliances_opex(PeriodEnum.WEEKLY)
        mock_scale_daily_to_period.assert_called_once_with(
            self.opex_daily, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, mock_scale_daily_to_period
    ):
        get_other_appliances_opex()
        mock_scale_daily_to_period.assert_called_once_with(
            self.opex_daily, PeriodEnum.DAILY
        )

    def test_it_returns_opex_per_period(self, _):
        result = get_other_appliances_opex()
        assert result == 86.42


class TestGetVehicleOpexPerDay(TestCase):
    petrol = 31.4 * 0.28884
    ev = 7.324 * 0.26175

    expected_weighted_opex_daily_petrol = petrol * (250 / 210)
    expected_weighted_opex_daily_ev = ev * (250 / 210) + (76 * 250 * 52 / 1000) / 365.25

    def test_it_calculates_daily_opex_for_one_petrol_car(self):
        result = get_vehicle_opex([mock_vehicle_petrol])
        assert result == self.petrol * (250 / 210)

    def test_it_calculates_daily_opex_for_one_diesel_car(self):
        result = get_vehicle_opex([mock_vehicle_diesel])
        daily_rucs = (76 * 50 * 52 / 1000) / 365.25
        expected = 22.8 * 0.19679 * 50 / 210 + daily_rucs
        assert result == expected

    def test_it_calculates_daily_opex_for_one_ev(self):
        result = get_vehicle_opex([mock_vehicle_ev])
        daily_rucs = (76 * 250 * 52 / 1000) / 365.25
        assert result == self.ev * (250 / 210) + daily_rucs

    def test_it_calculates_daily_opex_for_one_hybrid(self):
        result = get_vehicle_opex([mock_vehicle_hev])
        expected = (self.petrol * 0.7 + self.ev * 0.3) * (150 / 210)
        assert result == expected

    def test_it_calculates_daily_opex_for_one_plugin_hybrid(self):
        result = get_vehicle_opex([mock_vehicle_phev])
        daily_rucs = (38 * 175 * 52 / 1000) / 365.25
        expected = (self.petrol * 0.6 + self.ev * 0.4) * (175 / 210) + daily_rucs
        assert result == expected

    def test_it_combines_vehicles_correctly(self):
        result = get_vehicle_opex(
            [
                mock_vehicle_petrol,
                mock_vehicle_diesel,
                mock_vehicle_ev,
                mock_vehicle_hev,
                mock_vehicle_phev,
            ]
        )
        expected = (
            # petrol
            (31.4 * 0.28884 * (250 / 210))
            # diesel + RUC
            + (22.8 * 0.19679 * (50 / 210))
            + (76 * 50 * 52 / 1000) / 365.25
            # EV + RUC
            + (7.324 * 0.26175 * (250 / 210))
            + (76 * 250 * 52 / 1000) / 365.25
            # HEV
            + (self.petrol * 0.7 + self.ev * 0.3) * (150 / 210)
            # PHEV + RUC
            + (self.petrol * 0.6 + self.ev * 0.4) * (175 / 210)
            + (38 * 175 * 52 / 1000) / 365.25
        )
        assert result == expected

    @patch(
        "savings.opex.get_machine_opex.scale_daily_to_period",
    )
    def test_it_calls_scale_daily_to_period_correctly(self, mock_scale_daily_to_period):

        get_vehicle_opex([mock_vehicle_ev, mock_vehicle_petrol], PeriodEnum.WEEKLY)

        assert len(mock_scale_daily_to_period.call_args_list) == 2
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_opex_daily_petrol,
            PeriodEnum.WEEKLY,
        )
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_opex_daily_ev, PeriodEnum.WEEKLY
        )

    @patch(
        "savings.opex.get_machine_opex.scale_daily_to_period",
    )
    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, mock_scale_daily_to_period
    ):
        get_vehicle_opex([mock_vehicle_ev, mock_vehicle_petrol])
        assert len(mock_scale_daily_to_period.call_args_list) == 2
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_opex_daily_petrol,
            PeriodEnum.DAILY,
        )
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_opex_daily_ev, PeriodEnum.DAILY
        )

    def test_it_returns_opex_with_default_period(self):
        result = get_vehicle_opex([mock_vehicle_ev, mock_vehicle_petrol])

        assert (
            result
            == self.expected_weighted_opex_daily_petrol
            + self.expected_weighted_opex_daily_ev
        )

    def test_it_returns_opex_with_specified_period(self):
        result = get_vehicle_opex(
            [mock_vehicle_ev, mock_vehicle_petrol], PeriodEnum.WEEKLY
        )
        expected = (
            self.expected_weighted_opex_daily_petrol
            + self.expected_weighted_opex_daily_ev
        ) * 7
        assert pytest.approx(result) == expected


def get_mock_opex_values(fuel_type, vehicle_info):
    # Return fixed values for testing
    if fuel_type == VehicleFuelTypeEnum.PETROL:
        return 100.0  # $100 per day for petrol
    if fuel_type == VehicleFuelTypeEnum.ELECTRIC:
        return 50.0  # $50 per day for electric
    return 0.0


@patch(
    "savings.opex.get_machine_opex.get_energy_per_day", side_effect=get_mock_opex_values
)
class TestGetHybridOpexPerDay:
    def test_plug_in_hybrid(self, _):
        result = _get_hybrid_opex_per_day(VehicleFuelTypeEnum.PLUG_IN_HYBRID)
        # PHEV: 60% of petrol ($100) + 40% of electric ($50)
        # 60.0 + 20.0 = 80.0
        assert result == 80.0

    def test_hybrid(self, _):
        result = _get_hybrid_opex_per_day(VehicleFuelTypeEnum.HYBRID)
        # HEV: 70% of petrol ($100) + 30% of electric ($50)
        # 70.0 + 15.0 = 85.0
        assert result == 85.0

    def test_different_opex_values(self, mock_opex_values):
        # Override the mock for this specific test
        mock_opex_values.side_effect = lambda fuel_type, vehicle_info: {
            VehicleFuelTypeEnum.PETROL: 200.0,
            VehicleFuelTypeEnum.ELECTRIC: 100.0,
        }.get(fuel_type, 0.0)

        phev_result = _get_hybrid_opex_per_day(VehicleFuelTypeEnum.PLUG_IN_HYBRID)
        hev_result = _get_hybrid_opex_per_day(VehicleFuelTypeEnum.HYBRID)

        # PHEV: 60% of 200 + 40% of 100 = 120 + 40 = 160
        assert phev_result == 160.0

        # HEV: 70% of 200 + 30% of 100 = 140 + 30 = 170
        assert hev_result == 170.0

    def test_wrong_type_raises_type_error(self, mock_get_opex):
        with pytest.raises(TypeError, match="vehicle_type must be VehicleFuelTypeEnum"):
            _get_hybrid_opex_per_day("HYBRID")

    def test_non_hybrid_vehicle_type_raises_value_error(self, mock_get_opex):
        with pytest.raises(
            ValueError, match="vehicle_type must be PLUG_IN_HYBRID or HYBRID"
        ):
            _get_hybrid_opex_per_day(VehicleFuelTypeEnum.PETROL)
