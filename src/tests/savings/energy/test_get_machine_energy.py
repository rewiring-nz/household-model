from unittest import TestCase
from unittest.mock import patch

from openapi_client.models import (
    SpaceHeatingEnum,
    CooktopEnum,
)

from constants.fuel_stats import (
    FuelTypeEnum,
)
from constants.machines.machine_info import MachineInfoMap
from constants.machines.cooktop import COOKTOP_INFO
from constants.machines.space_heating import SPACE_HEATING_INFO
from constants.utils import PeriodEnum
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum
from savings.energy.get_machine_energy import (
    get_energy_per_day,
    get_energy_per_period,
    get_other_appliances_energy_per_period,
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
    "savings.energy.get_machine_energy.scale_daily_to_period",
    return_value=mock_energy_weekly,
)
@patch(
    "savings.energy.get_machine_energy.get_energy_per_day",
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
    "savings.energy.get_machine_energy.scale_daily_to_period",
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
