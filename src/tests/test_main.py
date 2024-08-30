from main import calculate_household_savings
from unittest.mock import patch
from unittest import TestCase
from tests.mocks import mock_household, mock_emissions


@patch("main.calculate_emissions", return_value=mock_emissions)
class TestCalculateHouseholdSavings(TestCase):
    def test_it_calls_calculate_emissions_correctly(self, mock_calculate_emissions):
        calculate_household_savings(mock_household)
        mock_calculate_emissions.assert_called_once_with(mock_household)
