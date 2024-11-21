from openapi_client.models import VehicleFuelTypeEnum, Vehicle
from constants.utils import DAYS_PER_YEAR, PeriodEnum
from params import OPERATIONAL_LIFETIME

from savings.opex.calculate_opex import get_rucs


class TestGetRucs:
    def test_single_diesel_vehicle_daily(self):
        vehicles = [
            Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=100)
        ]  # 100 km/week
        result = get_rucs(vehicles)
        expected = round(76 * 100 * 52 / 1000 / 365.25, 2)  # 1.08
        assert result == expected

    def test_single_diesel_vehicle_yearly(self):
        vehicles = [Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=100)]
        result = get_rucs(vehicles, PeriodEnum.YEARLY)
        assert result == round(76 * 100 * 52 / 1000, 2)

    def test_single_phev_vehicle_daily(self):
        vehicles = [
            Vehicle(fuel_type=VehicleFuelTypeEnum.PLUG_IN_HYBRID, kms_per_week=100)
        ]  # 100 km/week
        result = get_rucs(vehicles)
        expected = round(38 * 100 * 52 / 1000 / 365.25, 2)  # 0.54
        assert result == expected

    def test_single_ev_vehicle_daily(self):
        vehicles = [
            Vehicle(fuel_type=VehicleFuelTypeEnum.ELECTRIC, kms_per_week=100)
        ]  # 100 km/week
        result = get_rucs(vehicles)
        expected = round(76 * 100 * 52 / 1000 / 365.25, 2)  # 1.08
        assert result == expected

    def test_multiple_vehicles_different_fuels(self):
        vehicles = [
            Vehicle(fuel_type=VehicleFuelTypeEnum.PETROL, kms_per_week=100),
            Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=200),
            Vehicle(fuel_type=VehicleFuelTypeEnum.PLUG_IN_HYBRID, kms_per_week=250),
            Vehicle(fuel_type=VehicleFuelTypeEnum.ELECTRIC, kms_per_week=150),
        ]
        result = get_rucs(vehicles)

        expected = round(
            (76 * 200 * 52 / 1000 / 365.25)
            + (38 * 250 * 52 / 1000 / 365.25)
            + (76 * 150 * 52 / 1000 / 365.25),
            2,
        )
        assert result == expected

    def test_empty_vehicle_list(self):
        result = get_rucs([])
        assert result == 0

    def test_zero_kms_vehicle(self):
        vehicles = [Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=0)]
        result = get_rucs(vehicles)
        assert result == 0

    def test_very_high_kms(self):
        vehicles = [
            Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=10000)
        ]  # 10,000 km/week
        result = get_rucs(vehicles)
        assert result == round(76 * 10000 * 52 / 1000 / 365.25, 2)

    def test_all_periods(self):
        vehicles = [Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=100)]
        daily = get_rucs(vehicles, PeriodEnum.DAILY)
        weekly = get_rucs(vehicles, PeriodEnum.WEEKLY)
        yearly = get_rucs(vehicles, PeriodEnum.YEARLY)
        lifetime = get_rucs(vehicles, PeriodEnum.OPERATIONAL_LIFETIME)

        expected_daily = 76 * 100 * 52 / 1000 / 365.25
        assert daily == round(expected_daily, 2)
        assert weekly == round(expected_daily * 7, 2)
        assert yearly == round(expected_daily * DAYS_PER_YEAR, 2)
        assert lifetime == round(
            expected_daily * DAYS_PER_YEAR * OPERATIONAL_LIFETIME, 2
        )

    def test_multiple_identical_vehicles(self):
        vehicles = [
            Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=100),
            Vehicle(fuel_type=VehicleFuelTypeEnum.DIESEL, kms_per_week=100),
        ]
        result = get_rucs(vehicles)
        assert result == round(76 * 100 * 52 / 1000 / 365.25 * 2, 2)
