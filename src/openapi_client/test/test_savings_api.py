# coding: utf-8

"""
    Household savings

    This is the API for a household savings model. You can provide details about a household's energy use, and receive information about the household's potential emissions & cost savings from electrifying their fossil fuel machines, as well as the upfront costs of switching.

    The version of the OpenAPI document: 0.0.2
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from openapi_client.api.savings_api import SavingsApi  # noqa: E501


class TestSavingsApi(unittest.TestCase):
    """SavingsApi unit test stubs"""

    def setUp(self) -> None:
        self.api = SavingsApi()  # noqa: E501

    def tearDown(self) -> None:
        pass

    def test_calculate_savings(self) -> None:
        """Test case for calculate_savings

        Calculate savings & get upfront cost  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()