from unittest import TestCase
from unittest.mock import patch

import pytest

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
    _get_hybrid_energy_per_day,
    get_total_appliance_energy,
    get_vehicle_energy,
)
from tests.mocks import (
    mock_household,
    mock_vehicle_petrol,
    mock_vehicle_diesel,
    mock_vehicle_ev,
    mock_vehicle_hev,
    mock_vehicle_phev,
)

mock_energy_daily = {
    FuelTypeEnum.ELECTRICITY: 2.5,
}
mock_energy_weekly = {
    FuelTypeEnum.ELECTRICITY: 17.5,  # 12.345 * 7
}


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
    return_value=mock_energy_weekly[FuelTypeEnum.ELECTRICITY],
)
@patch(
    "savings.energy.get_machine_energy.get_energy_per_day",
    return_value=mock_energy_daily,
)
class TestGetEnergyPerPeriod:
    def test_it_calls_get_energy_per_day_correctly(self, mock_get_energy_per_day, _):
        get_energy_per_period(mock_household.space_heating, SPACE_HEATING_INFO, 1)
        mock_get_energy_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO, 1
        )

    def test_it_calls_get_energy_per_day_correctly_with_defaults(
        self, mock_get_energy_per_day, _
    ):
        get_energy_per_period(mock_household.space_heating, SPACE_HEATING_INFO)
        mock_get_energy_per_day.assert_called_once_with(
            SpaceHeatingEnum.WOOD, SPACE_HEATING_INFO, None
        )

    def test_it_calls_scale_daily_to_period_correctly(
        self, _, mock_scale_daily_to_period
    ):
        get_energy_per_period(
            mock_household.cooktop, COOKTOP_INFO, 1, PeriodEnum.WEEKLY
        )
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily[FuelTypeEnum.ELECTRICITY], PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, _, mock_scale_daily_to_period
    ):
        get_energy_per_period(mock_household.cooktop, COOKTOP_INFO)
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily[FuelTypeEnum.ELECTRICITY], PeriodEnum.DAILY
        )

    def test_it_calls_scale_daily_to_period_per_fuel_type(
        self, mock_get_energy_per_day, mock_scale_daily_to_period
    ):
        mock_get_energy_per_day.side_effect = [
            {
                FuelTypeEnum.ELECTRICITY: 2,
                FuelTypeEnum.PETROL: 3,
            }
        ]

        get_energy_per_period(mock_household.cooktop, COOKTOP_INFO)
        assert len(mock_scale_daily_to_period.call_args_list) == 2
        mock_scale_daily_to_period.assert_any_call(2, PeriodEnum.DAILY)
        mock_scale_daily_to_period.assert_any_call(3, PeriodEnum.DAILY)

    def test_it_returns_energy_per_period(self, _, __):
        result = get_energy_per_period(mock_household.space_heating, SPACE_HEATING_INFO)
        assert result == mock_energy_weekly


@patch(
    "savings.energy.get_machine_energy.get_energy_per_period",
    side_effect=[
        {
            FuelTypeEnum.ELECTRICITY: 1,
            FuelTypeEnum.NATURAL_GAS: 5,
            FuelTypeEnum.LPG: 3,
            FuelTypeEnum.WOOD: 4,
            FuelTypeEnum.PETROL: 0.5,
            FuelTypeEnum.DIESEL: 7,
        },
        {
            FuelTypeEnum.ELECTRICITY: 2,
            FuelTypeEnum.NATURAL_GAS: 10,
            FuelTypeEnum.LPG: 6,
            FuelTypeEnum.WOOD: 4.5,
            FuelTypeEnum.PETROL: 0.5,
            FuelTypeEnum.DIESEL: 8,
        },
        {
            FuelTypeEnum.ELECTRICITY: 3,
            FuelTypeEnum.NATURAL_GAS: 15,
            FuelTypeEnum.LPG: 9,
            FuelTypeEnum.WOOD: 5,
            FuelTypeEnum.PETROL: 0.5,
            FuelTypeEnum.DIESEL: 9,
        },
    ],
)
class TestGetTotalApplianceEnergy:
    def test_it_combines_fuel_types_correctly(self, mock_get_energy_per_period):
        result = get_total_appliance_energy(mock_household, PeriodEnum.DAILY)
        expected = {
            FuelTypeEnum.ELECTRICITY: 6,
            FuelTypeEnum.NATURAL_GAS: 30,
            FuelTypeEnum.LPG: 18,
            FuelTypeEnum.WOOD: 13.5,
            FuelTypeEnum.PETROL: 1.5,
            FuelTypeEnum.DIESEL: 24,
        }
        assert result == expected

    def test_it_works_if_fuel_types_missing(self, mock_get_energy_per_period):
        mock_get_energy_per_period.side_effect = [
            {
                FuelTypeEnum.ELECTRICITY: 1,
                FuelTypeEnum.NATURAL_GAS: 0,
                FuelTypeEnum.LPG: 0,
                FuelTypeEnum.WOOD: 0,
                # FuelTypeEnum.PETROL: 0.5,
                # FuelTypeEnum.DIESEL: 7,
            },
            {
                FuelTypeEnum.ELECTRICITY: 2,
                FuelTypeEnum.NATURAL_GAS: 0,
                FuelTypeEnum.LPG: 0,
                FuelTypeEnum.WOOD: 0,
                FuelTypeEnum.PETROL: 0.5,
                # FuelTypeEnum.DIESEL: 8,
            },
            {
                FuelTypeEnum.ELECTRICITY: 3,
                FuelTypeEnum.NATURAL_GAS: 0,
                FuelTypeEnum.LPG: 0,
                FuelTypeEnum.WOOD: 0,
                FuelTypeEnum.PETROL: 0.5,
                # FuelTypeEnum.DIESEL: 9,
            },
        ]
        result = get_total_appliance_energy(mock_household, PeriodEnum.DAILY)
        expected = {
            FuelTypeEnum.ELECTRICITY: 6,
            FuelTypeEnum.NATURAL_GAS: 0,
            FuelTypeEnum.LPG: 0,
            FuelTypeEnum.WOOD: 0,
            FuelTypeEnum.PETROL: 1.0,
            FuelTypeEnum.DIESEL: 0,  # Still includes a key for it with zero value
        }
        assert result == expected


@patch(
    "savings.energy.get_machine_energy.scale_daily_to_period",
    return_value=mock_energy_weekly[FuelTypeEnum.ELECTRICITY],
)
@patch(
    "savings.energy.get_machine_energy.scale_energy_by_occupancy",
    return_value=mock_energy_daily[FuelTypeEnum.ELECTRICITY],
)
class TestGetOtherAppliancesEnergyPerPeriod:
    energy = 0.34 + 4.05 + 2.85

    def test_it_calls_scale_energy_by_occupancy_correctly(
        self, mock_scale_energy_by_occupancy, mock_scale_daily_to_period
    ):
        get_other_appliances_energy_per_period(1, PeriodEnum.WEEKLY)
        mock_scale_energy_by_occupancy.assert_called_once_with(self.energy, 1)

    def test_it_calls_scale_energy_by_occupancy_correctly_with_default(
        self, mock_scale_energy_by_occupancy, mock_scale_daily_to_period
    ):
        get_other_appliances_energy_per_period()
        mock_scale_energy_by_occupancy.assert_called_once_with(self.energy, None)

    def test_it_calls_scale_daily_to_period_correctly(
        self, mock_scale_energy_by_occupancy, mock_scale_daily_to_period
    ):
        get_other_appliances_energy_per_period(None, PeriodEnum.WEEKLY)
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily[FuelTypeEnum.ELECTRICITY], PeriodEnum.WEEKLY
        )

    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, mock_scale_energy_by_occupancy, mock_scale_daily_to_period
    ):
        get_other_appliances_energy_per_period()
        mock_scale_daily_to_period.assert_called_once_with(
            mock_energy_daily[FuelTypeEnum.ELECTRICITY], PeriodEnum.DAILY
        )

    def test_it_returns_energy_per_period(self, _, __):
        assert get_other_appliances_energy_per_period(1, PeriodEnum.WEEKLY) == {
            FuelTypeEnum.ELECTRICITY: 17.5
        }
        assert get_other_appliances_energy_per_period() == {
            FuelTypeEnum.ELECTRICITY: 17.5
        }


class TestGetVehicleEnergyPerDay(TestCase):
    # kWh per day for average mileage
    petrol = 31.4
    ev = 7.324

    expected_weighted_energy_daily_petrol = petrol * (250 / 210)
    expected_weighted_energy_daily_ev = ev * (250 / 210)

    def test_it_calculates_daily_energy_for_one_petrol_car(self):
        result = get_vehicle_energy([mock_vehicle_petrol])
        assert result == self.expected_weighted_energy_daily_petrol

    def test_it_calculates_daily_energy_for_one_diesel_car(self):
        result = get_vehicle_energy([mock_vehicle_diesel])
        expected = 22.8 * 50 / 210
        assert result == expected

    def test_it_calculates_daily_energy_for_one_ev(self):
        result = get_vehicle_energy([mock_vehicle_ev])
        assert result == self.ev * (250 / 210)

    def test_it_calculates_daily_energy_for_one_hybrid(self):
        result = get_vehicle_energy([mock_vehicle_hev])
        expected = (self.petrol * 0.7 + self.ev * 0.3) * (150 / 210)
        assert result == expected

    def test_it_calculates_daily_energy_for_one_plugin_hybrid(self):
        result = get_vehicle_energy([mock_vehicle_phev])
        expected = (self.petrol * 0.6 + self.ev * 0.4) * (175 / 210)
        assert result == expected

    def test_it_combines_vehicles_correctly(self):
        result = get_vehicle_energy(
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
            (31.4 * (250 / 210))
            # diesel
            + (22.8 * (50 / 210))
            # EV
            + (7.324 * (250 / 210))
            # HEV
            + (self.petrol * 0.7 + self.ev * 0.3) * (150 / 210)
            # PHEV
            + (self.petrol * 0.6 + self.ev * 0.4) * (175 / 210)
        )
        assert result == expected

    @patch(
        "savings.energy.get_machine_energy.scale_daily_to_period",
    )
    def test_it_calls_scale_daily_to_period_correctly(self, mock_scale_daily_to_period):

        get_vehicle_energy([mock_vehicle_ev, mock_vehicle_petrol], PeriodEnum.WEEKLY)

        assert len(mock_scale_daily_to_period.call_args_list) == 2
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_energy_daily_petrol,
            PeriodEnum.WEEKLY,
        )
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_energy_daily_ev, PeriodEnum.WEEKLY
        )

    @patch(
        "savings.energy.get_machine_energy.scale_daily_to_period",
    )
    def test_it_calls_scale_daily_to_period_correctly_with_default(
        self, mock_scale_daily_to_period
    ):
        get_vehicle_energy([mock_vehicle_ev, mock_vehicle_petrol])
        assert len(mock_scale_daily_to_period.call_args_list) == 2
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_energy_daily_petrol,
            PeriodEnum.DAILY,
        )
        mock_scale_daily_to_period.assert_any_call(
            self.expected_weighted_energy_daily_ev, PeriodEnum.DAILY
        )

    def test_it_returns_energy_with_default_period(self):
        result = get_vehicle_energy([mock_vehicle_ev, mock_vehicle_petrol])

        assert (
            result
            == self.expected_weighted_energy_daily_petrol
            + self.expected_weighted_energy_daily_ev
        )

    def test_it_returns_energy_with_specified_period(self):
        result = get_vehicle_energy(
            [mock_vehicle_ev, mock_vehicle_petrol], PeriodEnum.WEEKLY
        )
        expected = (
            self.expected_weighted_energy_daily_petrol
            + self.expected_weighted_energy_daily_ev
        ) * 7
        assert pytest.approx(result) == expected


def get_mock_energy_values(fuel_type, vehicle_info):
    # Return fixed values for testing
    if fuel_type == VehicleFuelTypeEnum.PETROL:
        return 30.0  # 30 kWh per day for petrol
    if fuel_type == VehicleFuelTypeEnum.ELECTRIC:
        return 5.0  # 5 kWh per day for electric
    return 0.0


@patch(
    "savings.energy.get_machine_energy.get_energy_per_day",
    side_effect=get_mock_energy_values,
)
class TestGetHybridEnergyPerDay:
    def test_plug_in_hybrid(self, _):
        result = _get_hybrid_energy_per_day(VehicleFuelTypeEnum.PLUG_IN_HYBRID)
        # PHEV: 60% of petrol (30 kWh) + 40% of electric (5 kWh) = 18 + 2
        assert result == 20.0

    def test_hybrid(self, _):
        result = _get_hybrid_energy_per_day(VehicleFuelTypeEnum.HYBRID)
        # HEV: 70% of petrol (30 kWh) + 30% of electric (5 kWh) = 21 + 1.5
        assert result == 22.5

    def test_different_energy_values(self, mock_energy_values):
        # Override the mock for this specific test
        mock_energy_values.side_effect = lambda fuel_type, vehicle_info: {
            VehicleFuelTypeEnum.PETROL: 200.0,
            VehicleFuelTypeEnum.ELECTRIC: 30.0,
        }.get(fuel_type, 0.0)

        phev_result = _get_hybrid_energy_per_day(VehicleFuelTypeEnum.PLUG_IN_HYBRID)
        hev_result = _get_hybrid_energy_per_day(VehicleFuelTypeEnum.HYBRID)

        # PHEV: 60% of 200 + 40% of 30 = 120 + 12 = 132
        assert phev_result == 132.0

        # HEV: 70% of 200 + 30% of 30 = 140 + 9 = 149
        assert hev_result == 149.0

    def test_wrong_type_raises_type_error(self, mock_get_energy):
        with pytest.raises(TypeError, match="vehicle_type must be VehicleFuelTypeEnum"):
            _get_hybrid_energy_per_day("HYBRID")

    def test_non_hybrid_vehicle_type_raises_value_error(self, mock_get_energy):
        with pytest.raises(
            ValueError, match="vehicle_type must be PLUG_IN_HYBRID or HYBRID"
        ):
            _get_hybrid_energy_per_day(VehicleFuelTypeEnum.PETROL)
