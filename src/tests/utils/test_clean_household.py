from openapi_client.models.household import Household
from openapi_client.models.vehicle import Vehicle
from openapi_client.models.vehicle_fuel_type_enum import VehicleFuelTypeEnum
from utils.clean_household import clean_household, clean_vehicle
from tests.mocks import mock_vehicle_petrol

from unittest import TestCase
from unittest.mock import patch, call


class TestCleanHousehold(TestCase):

    @patch("utils.clean_household.clean_vehicle")
    def test_clean_household_no_vehicles(self, mock_clean_vehicle):
        cleaned_household = clean_household(Household(vehicles=[]))
        self.assertEqual(cleaned_household.vehicles, [])
        mock_clean_vehicle.assert_not_called()

    @patch("utils.clean_household.clean_vehicle")
    def test_clean_household_single_vehicle(self, mock_clean_vehicle):
        vehicle = Vehicle(fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=None)
        cleaned_vehicle = Vehicle(
            fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=123
        )
        mock_clean_vehicle.return_value = cleaned_vehicle

        cleaned_household = clean_household(Household(vehicles=[vehicle]))

        mock_clean_vehicle.assert_called_once_with(vehicle)
        self.assertEqual(len(cleaned_household.vehicles), 1)
        self.assertEqual(cleaned_household.vehicles[0].kms_per_week, 123)

    @patch("utils.clean_household.clean_vehicle")
    def test_clean_household_multiple_vehicles(self, mock_clean_vehicle):
        vehicle1 = Vehicle(fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=None)
        vehicle2 = Vehicle(fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=500)
        cleaned_vehicle1 = Vehicle(
            fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=123
        )
        cleaned_vehicle2 = Vehicle(
            fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=500
        )
        mock_clean_vehicle.side_effect = [cleaned_vehicle1, cleaned_vehicle2]

        cleaned_household = clean_household(Household(vehicles=[vehicle1, vehicle2]))

        self.assertEqual(len(cleaned_household.vehicles), 2)
        self.assertEqual(cleaned_household.vehicles[0].kms_per_week, 123)
        self.assertEqual(cleaned_household.vehicles[1].kms_per_week, 500)
        mock_clean_vehicle.assert_has_calls([call(vehicle1), call(vehicle2)])


class TestCleanVehicle(TestCase):
    def test_it_replaces_null_kms_with_avg(self):
        assert clean_vehicle(
            Vehicle(
                fuelType=VehicleFuelTypeEnum.PETROL,
                kms_per_week=None,
                switchToEV=False,
            )
        ) == Vehicle(
            fuelType=VehicleFuelTypeEnum.PETROL,
            kms_per_week=round(11000 / 52),
            switchToEV=False,
        )

    def test_it_does_not_change_if_kms_present(self):
        assert clean_vehicle(mock_vehicle_petrol) == mock_vehicle_petrol
