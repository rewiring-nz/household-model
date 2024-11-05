import unittest
from unittest.mock import patch
from savings.emissions.calculate_emissions import calculate_emissions
from constants.utils import PeriodEnum
from params import OPERATIONAL_LIFETIME
from tests.mocks import mock_household, mock_household_electrified


class TestCalculateEmissions(unittest.TestCase):

    get_appliance_emissions_side_effect = lambda self, household, info, period: {
        PeriodEnum.WEEKLY: 1.0,
        PeriodEnum.YEARLY: 52.0,
        PeriodEnum.OPERATIONAL_LIFETIME: 500.0,
    }.get(period, 0.0)

    get_vehicle_emissions_side_effect = lambda self, vehicles, period: {
        PeriodEnum.WEEKLY: 2.0,
        PeriodEnum.YEARLY: 104.0,
        PeriodEnum.OPERATIONAL_LIFETIME: 7000.0,
    }.get(period, 0.0)

    get_other_emissions_side_effect = lambda self, period: {
        PeriodEnum.WEEKLY: 0.5,
        PeriodEnum.YEARLY: 26.5,
        PeriodEnum.OPERATIONAL_LIFETIME: 2000.0,
    }.get(period, 0.0)

    @patch("savings.emissions.calculate_emissions.get_appliance_emissions")
    @patch("savings.emissions.calculate_emissions.get_vehicle_emissions")
    @patch("savings.emissions.calculate_emissions.get_other_appliance_emissions")
    def test_calculate_emissions_sums_correctly(
        self, mock_get_other, mock_get_vehicle, mock_get_appliance
    ):
        mock_get_appliance.side_effect = self.get_appliance_emissions_side_effect
        mock_get_vehicle.side_effect = self.get_vehicle_emissions_side_effect
        mock_get_other.side_effect = self.get_other_emissions_side_effect

        result = calculate_emissions(mock_household, mock_household_electrified)

        self.assertEqual(result.per_week.before, 1.0 + 1.0 + 1.0 + 2.0 + 0.5)
        self.assertEqual(result.per_week.after, 1.0 + 1.0 + 1.0 + 2.0 + 0.5)
        self.assertEqual(result.per_week.difference, 0.0)

        self.assertEqual(result.per_year.before, 52.0 + 52.0 + 52.0 + 104.0 + 26.5)
        self.assertEqual(result.per_year.after, 52.0 + 52.0 + 52.0 + 104.0 + 26.5)
        self.assertEqual(result.per_year.difference, 0.0)

        self.assertEqual(
            result.over_lifetime.before, 500.0 + 500.0 + 500.0 + 7000.0 + 2000.0
        )
        self.assertEqual(
            result.over_lifetime.after, 500.0 + 500.0 + 500.0 + 7000.0 + 2000.0
        )
        self.assertEqual(result.over_lifetime.difference, 0.0)

        self.assertEqual(result.operational_lifetime, OPERATIONAL_LIFETIME)

    def test_calculate_emissions_real_values(self):
        result = calculate_emissions(mock_household, mock_household_electrified)

        before = {
            "space_heating_wood": 14.44 * 0.016,
            "water_heating_gas": 6.6 * 0.201,
            "cooktop_resistance": 0.83 * 0.074,
            "petrol_car": 31.4 * 0.258 * (250 * 52 / 11000),
            "diesel_car": 22.8 * 0.253 * (50 * 52 / 11000),
            "other": (0.34 + 4.48 + 3.06) * 0.074,
        }
        after = {
            "space_heating_heat_pump": 2.3 * 0.074,
            "water_heating_heat_pump": 1.71 * 0.074,
            "cooktop_resistance": 0.83 * 0.074,  # didn't swap
            "ev_car": 7.324 * 0.074 * (250 * 52 / 11000),
            "diesel_car": 22.8 * 0.253 * (50 * 52 / 11000),  # didn't want to switch
            "other": (0.34 + 4.48 + 3.06) * 0.074,
        }
        before_daily = sum(before.values())
        after_daily = sum(after.values())
        difference_daily = after_daily - before_daily

        self.assertAlmostEqual(result.per_week.before, before_daily * 7, 2)
        self.assertAlmostEqual(result.per_week.after, after_daily * 7, 2)
        self.assertAlmostEqual(result.per_week.difference, difference_daily * 7, 2)

        self.assertAlmostEqual(result.per_year.before, before_daily * 365.25, 2)
        self.assertAlmostEqual(result.per_year.after, after_daily * 365.25, 2)
        self.assertAlmostEqual(result.per_year.difference, difference_daily * 365.25, 2)

        self.assertAlmostEqual(
            result.over_lifetime.before, before_daily * 365.25 * 15, 2
        )
        self.assertAlmostEqual(result.over_lifetime.after, after_daily * 365.25 * 15, 2)
        self.assertAlmostEqual(
            result.over_lifetime.difference, difference_daily * 365.25 * 15, 2
        )

        self.assertEqual(result.operational_lifetime, OPERATIONAL_LIFETIME)
