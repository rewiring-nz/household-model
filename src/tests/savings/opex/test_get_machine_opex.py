from unittest import TestCase
from unittest.mock import patch

from openapi_client.models import (
    SpaceHeatingEnum,
    CooktopEnum,
    WaterHeatingEnum,
)

from constants.fuel_stats import (
    COST_PER_FUEL_KWH_TODAY,
    EMISSIONS_FACTORS,
    FuelTypeEnum,
)
from constants.machines.machine_info import MachineInfoMap
from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.water_heating import WATER_HEATING_INFO
from constants.machines.space_heating import SPACE_HEATING_INFO
from constants.utils import PeriodEnum
from savings.opex.get_machine_opex import (
    get_appliance_opex,
    scale_daily_to_period,
    get_opex_per_day,
    get_other_appliance_opex,
    get_vehicle_opex,
)
from tests.mocks import (
    mock_household,
    mock_vehicle_petrol,
    mock_vehicle_diesel,
    mock_vehicle_ev,
    mock_vehicle_hev,
    mock_vehicle_phev,
)

mock_opex_daily = 12.345
mock_opex_weekly = 86.415  # 12.345 * 7


class TestGetOpexPerDay(TestCase):
    mock_appliance_info: MachineInfoMap = {
        CooktopEnum.GAS: {"kwh_per_day": 10.0, "fuel_type": FuelTypeEnum.NATURAL_GAS},
        SpaceHeatingEnum.ELECTRIC_HEAT_PUMP: {
            "kwh_per_day": 5.0,
            "fuel_type": FuelTypeEnum.ELECTRICITY,
        },
    }

    def test_get_opex_per_day_gas_cooktop(self):
        opex = get_opex_per_day(CooktopEnum.GAS, self.mock_appliance_info)
        expected_opex = 10.0 * COST_PER_FUEL_KWH_TODAY[FuelTypeEnum.NATURAL_GAS]
        assert opex == expected_opex

    def test_get_opex_per_day_electric_heat_pump(self):
        opex = get_opex_per_day(
            SpaceHeatingEnum.ELECTRIC_HEAT_PUMP, self.mock_appliance_info
        )
        expected_opex = 5.0 * COST_PER_FUEL_KWH_TODAY[FuelTypeEnum.ELECTRICITY]
        assert opex == expected_opex

    def test_get_opex_per_day_handles_missing_fuel_type(self):
        mock_appliance_info = {
            CooktopEnum.GAS: {"kwh_per_day": 10.0, "fuel_type": None}
        }
        with self.assertRaises(KeyError):
            get_opex_per_day(CooktopEnum.GAS, mock_appliance_info)

    def test_get_opex_per_day_handles_missing_kwh_per_day(self):
        mock_appliance_info = {
            CooktopEnum.GAS: {
                "kwh_per_day": None,
                "fuel_type": FuelTypeEnum.NATURAL_GAS,
            }
        }
        with self.assertRaises(TypeError):
            get_opex_per_day(CooktopEnum.GAS, mock_appliance_info)

    def test_get_opex_per_day_handles_invalid_machine_type(self):
        invalid_machine_type = CooktopEnum.GAS
        invalid_mock_appliance_info = {}
        with self.assertRaises(KeyError):
            get_opex_per_day(invalid_machine_type, invalid_mock_appliance_info)


@patch(
    "savings.opex.get_machine_opex.scale_daily_to_period",
    return_value=mock_opex_weekly,
)
@patch(
    "savings.opex.get_machine_opex.get_opex_per_day",
    return_value=mock_opex_daily,
)
class TestGetApplianceOpex:
    def test_it_calls_get_opex_per_day_correctly(self, mock_get_opex_per_day, _):
        get_appliance_opex(mock_household.space_heating, SPACE_HEATING_INFO)
        mock_get_opex_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO
        )

    def test_it_calls_scale_daily_to_period_correctly(
        self, _, mock_scale_daily_to_period
    ):
        get_appliance_opex(mock_household.cooktop, COOKTOP_INFO, PeriodEnum.WEEKLY)
        mock_scale_daily_to_period.assert_called_once_with(
            mock_opex_daily, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, _, mock_scale_daily_to_period
    ):
        get_appliance_opex(mock_household.cooktop, COOKTOP_INFO)
        mock_scale_daily_to_period.assert_called_once_with(
            mock_opex_daily, PeriodEnum.DAILY
        )

    def test_it_returns_opex_per_period_rounded_to_2dp(self, _, __):
        result = get_appliance_opex(mock_household.space_heating, SPACE_HEATING_INFO)
        assert result == 86.42


@patch(
    "savings.opex.get_machine_opex.scale_daily_to_period",
    return_value=mock_opex_weekly,
)
class TestGetOtherApplianceOpex:
    opex_daily = (0.34 + 4.05 + 2.85) * 0.26175

    def test_it_calls_scale_daily_to_period_correctly(self, mock_scale_daily_to_period):
        get_other_appliance_opex(PeriodEnum.WEEKLY)
        mock_scale_daily_to_period.assert_called_once_with(
            self.opex_daily, PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, mock_scale_daily_to_period
    ):
        get_other_appliance_opex()
        mock_scale_daily_to_period.assert_called_once_with(
            self.opex_daily, PeriodEnum.DAILY
        )

    def test_it_returns_opex_per_period(self, _):
        result = get_other_appliance_opex()
        assert result == 86.42


# class TestGetVehicleOpexPerDay(TestCase):
#     petrol = 31.4 * 0.242
#     ev = 7.324 * 0.098

#     def test_it_calculates_daily_opex_for_one_petrol_car(self):
#         result = get_vehicle_opex([mock_vehicle_petrol])
#         assert result == self.petrol * (250 * 52 / 11000)

#     def test_it_calculates_daily_opex_for_one_diesel_car(self):
#         result = get_vehicle_opex([mock_vehicle_diesel])
#         expected = 22.8 * 0.253 * (50 * 52 / 11000)
#         assert result == expected

#     def test_it_calculates_daily_opex_for_one_ev(self):
#         result = get_vehicle_opex([mock_vehicle_ev])
#         assert result == self.ev * (250 * 52 / 11000)

#     def test_it_calculates_daily_opex_for_one_hybrid(self):
#         result = get_vehicle_opex([mock_vehicle_hev])
#         expected = (self.petrol * 0.7 + self.ev * 0.3) * (150 * 52 / 11000)
#         assert result == expected

#     def test_it_calculates_daily_opex_for_one_plugin_hybrid(self):
#         result = get_vehicle_opex([mock_vehicle_phev])
#         expected = (self.petrol * 0.6 + self.ev * 0.4) * (175 * 52 / 11000)
#         assert result == expected

#     def test_it_combines_vehicles_correctly(self):
#         result = get_vehicle_opex(
#             [
#                 mock_vehicle_petrol,
#                 mock_vehicle_diesel,
#                 mock_vehicle_ev,
#                 mock_vehicle_hev,
#                 mock_vehicle_phev,
#             ]
#         )
#         expected = (
#             (31.4 * 0.242 * (250 * 52 / 11000))
#             + (22.8 * 0.253 * (50 * 52 / 11000))
#             + (7.324 * 0.098 * (250 * 52 / 11000))
#             + (self.petrol * 0.7 + self.ev * 0.3) * (150 * 52 / 11000)
#             + (self.petrol * 0.6 + self.ev * 0.4) * (175 * 52 / 11000)
#         )
#         assert result == expected

#     @patch(
#         "savings.opex.get_machine_opex.scale_daily_to_period",
#     )
#     def test_it_calls_scale_daily_to_period_correctly(self, mock_scale_daily_to_period):
#         get_vehicle_opex([mock_vehicle_ev, mock_vehicle_petrol], PeriodEnum.WEEKLY)
#         assert len(mock_scale_daily_to_period.call_args_list) == 2
#         mock_scale_daily_to_period.assert_any_call(
#             self.petrol * (250 * 52 / 11000), PeriodEnum.WEEKLY
#         )
#         mock_scale_daily_to_period.assert_any_call(
#             self.ev * (250 * 52 / 11000), PeriodEnum.WEEKLY
#         )

#     @patch(
#         "savings.opex.get_machine_opex.scale_daily_to_period",
#     )
#     def test_it_calls_scale_daily_to_period_correctly_with_default(
#         self, mock_scale_daily_to_period
#     ):
#         get_vehicle_opex([mock_vehicle_ev, mock_vehicle_petrol])
#         assert len(mock_scale_daily_to_period.call_args_list) == 2
#         mock_scale_daily_to_period.assert_any_call(
#             self.petrol * (250 * 52 / 11000), PeriodEnum.DAILY
#         )
#         mock_scale_daily_to_period.assert_any_call(
#             self.ev * (250 * 52 / 11000), PeriodEnum.DAILY
#         )

#     def test_it_returns_opex_with_default_period(self):
#         result = get_vehicle_opex([mock_vehicle_ev, mock_vehicle_petrol])
#         assert result == (self.petrol * (250 * 52 / 11000)) + (
#             self.ev * (250 * 52 / 11000)
#         )

#     def test_it_returns_opex_with_specified_period(self):
#         result = get_vehicle_opex(
#             [mock_vehicle_ev, mock_vehicle_petrol], PeriodEnum.WEEKLY
#         )
#         assert (
#             result
#             == ((self.petrol * (250 * 52 / 11000)) + (self.ev * (250 * 52 / 11000))) * 7
#         )
