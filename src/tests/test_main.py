from main import calculate_household_savings
from unittest.mock import patch
from unittest import TestCase
from tests.mocks import (
    mock_household,
    mock_emissions,
    mock_opex,
    mock_upfront_cost,
    mock_recommendation,
)
from openapi_client.models import Savings


@patch("main.recommend_next_action", return_value=mock_recommendation)
@patch("main.calculate_upfront_cost", return_value=mock_upfront_cost)
@patch("main.calculate_opex", return_value=mock_opex)
@patch("main.calculate_emissions", return_value=mock_emissions)
class TestCalculateHouseholdSavings(TestCase):

    def test_it_calls_calculate_emissions_correctly(
        self,
        mock_calculate_emissions,
        mock_calculate_opex,
        mock_calculate_upfront_cost,
        mock_recommend_next_action,
    ):
        calculate_household_savings(mock_household)
        mock_calculate_emissions.assert_called_once_with(mock_household)

    def test_it_calls_calculate_opex_correctly(
        self,
        mock_calculate_emissions,
        mock_calculate_opex,
        mock_calculate_upfront_cost,
        mock_recommend_next_action,
    ):
        calculate_household_savings(mock_household)
        mock_calculate_opex.assert_called_once_with(mock_household)

    def test_it_calls_calculate_upfront_cost_correctly(
        self,
        mock_calculate_emissions,
        mock_calculate_opex,
        mock_calculate_upfront_cost,
        mock_recommend_next_action,
    ):
        calculate_household_savings(mock_household)
        mock_calculate_upfront_cost.assert_called_once_with(mock_household)

    def test_it_calls_recommend_next_action_correctly(
        self,
        mock_calculate_emissions,
        mock_calculate_opex,
        mock_calculate_upfront_cost,
        mock_recommend_next_action,
    ):
        calculate_household_savings(mock_household)
        mock_recommend_next_action.assert_called_once_with(mock_household)

    def test_it_returns_savings(
        self,
        mock_calculate_emissions,
        mock_calculate_opex,
        mock_calculate_upfront_cost,
        mock_recommend_next_action,
    ):
        result = calculate_household_savings(mock_household)
        assert result == Savings(
            emissions=mock_emissions,
            opex=mock_opex,
            upfrontCost=mock_upfront_cost,
            recommendation=mock_recommendation,
        )
