from unittest.mock import MagicMock, patch

from openapi_client.models import (
    CooktopEnum,
    Household,
    LocationEnum,
    Recommendation,
    RecommendationActionEnum,
    SpaceHeatingEnum,
    WaterHeatingEnum,
    Solar,
    Battery,
)

from models.recommend_next_action import n_vehicles_to_electrify, recommend_next_action
from openapi_client.models.vehicle import Vehicle
from tests.mocks import mock_vehicle_petrol, mock_vehicle_ev

base_household = {
    "location": LocationEnum.AUCKLAND_CENTRAL,
    "occupancy": 4,
    "space_heating": SpaceHeatingEnum.WOOD,
    "water_heating": WaterHeatingEnum.GAS,
    "cooktop": CooktopEnum.GAS,
    "vehicles": [
        mock_vehicle_petrol,
    ],
    "battery": Battery(hasBattery=False, installBattery=True),
}
electrified_household = {
    **base_household,
    "solar": Solar(hasSolar=True),
    "vehicles": [mock_vehicle_ev, mock_vehicle_ev],
    "space_heating": SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
    "water_heating": WaterHeatingEnum.ELECTRIC_HEAT_PUMP,
    "cooktop": CooktopEnum.ELECTRIC_INDUCTION,
    "battery": Battery(hasBattery=True),
}


class TestRecommendNextAction:
    def test_no_solar_and_wants_solar(self):
        # household without solar and wants solar
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=False, installSolar=True),
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.SOLAR,
            url="https://www.rewiring.nz/electrification-guides/solar",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_no_solar_and_does_not_want_solar(self):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=False, installSolar=False),
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.VEHICLE,
            url="https://www.rewiring.nz/electrification-guides/electric-cars",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_has_solar(self):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.SPACE_HEATING,
            url="https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_has_solar_and_electrified_first_vehicle(self):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
                "vehicles": [mock_vehicle_ev],
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.VEHICLE,
            url="https://www.rewiring.nz/electrification-guides/electric-cars",
        )
        result = recommend_next_action(household)
        assert result == expected

        # Same even if they have another petrol vehicle
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
                "vehicles": [mock_vehicle_ev, mock_vehicle_petrol],
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.SPACE_HEATING,
            url="https://www.rewiring.nz/electrification-guides/space-heating-and-cooling",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_has_solar_and_electrified_first_vehicle_and_space_heater(self):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
                "vehicles": [mock_vehicle_ev, mock_vehicle_petrol],
                "space_heating": SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.WATER_HEATING,
            url="https://www.rewiring.nz/electrification-guides/water-heating",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_has_solar_and_electrified_first_vehicle_and_space_heater_and_water_heater(
        self,
    ):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
                "vehicles": [mock_vehicle_ev, mock_vehicle_petrol],
                "space_heating": SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                "water_heating": WaterHeatingEnum.ELECTRIC_HEAT_PUMP,
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.COOKING,
            url="https://www.rewiring.nz/electrification-guides/cooktops",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_has_solar_and_electrified_all_appliances(self):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
                "vehicles": [mock_vehicle_ev, mock_vehicle_petrol],
                "space_heating": SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                "water_heating": WaterHeatingEnum.ELECTRIC_HEAT_PUMP,
                "cooktop": CooktopEnum.ELECTRIC_INDUCTION,
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.BATTERY,
            url="https://www.rewiring.nz/electrification-guides/home-batteries",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_has_solar_and_electrified_all_appliances_and_has_battery(self):
        household = Household(
            **{
                **base_household,
                "solar": Solar(hasSolar=True),
                "vehicles": [mock_vehicle_ev, mock_vehicle_petrol],
                "space_heating": SpaceHeatingEnum.ELECTRIC_HEAT_PUMP,
                "water_heating": WaterHeatingEnum.ELECTRIC_HEAT_PUMP,
                "cooktop": CooktopEnum.ELECTRIC_INDUCTION,
                "battery": Battery(hasBattery=True),
            }
        )
        expected = Recommendation(
            action=RecommendationActionEnum.VEHICLE,
            url="https://www.rewiring.nz/electrification-guides/electric-cars",
        )
        result = recommend_next_action(household)
        assert result == expected

    def test_it_keeps_electrifying_vehicles_until_all_electric(self):
        expected = Recommendation(
            action=RecommendationActionEnum.VEHICLE,
            url="https://www.rewiring.nz/electrification-guides/electric-cars",
        )
        for i in range(5):
            assert (
                recommend_next_action(
                    Household(
                        **{
                            **electrified_household,
                            "vehicles": [mock_vehicle_ev] * i + [mock_vehicle_petrol],
                        }
                    )
                )
                == expected
            )

    def test_has_fully_electrified(self):
        household = Household(**electrified_household)
        expected = Recommendation(action=RecommendationActionEnum.FULLY_ELECTRIFIED)
        result = recommend_next_action(household)
        assert result == expected


@patch("models.recommend_next_action.should_electrify")
class TestNVehiclesToElectrify:
    mock_vehicle1 = MagicMock(spec=Vehicle)
    mock_vehicle2 = MagicMock(spec=Vehicle)
    vehicles = [mock_vehicle1, mock_vehicle2]

    def test_all_vehicles_need_electrification(self, mock_should_electrify):
        mock_should_electrify.side_effect = [True, True]
        result = n_vehicles_to_electrify(self.vehicles)
        assert result == 2

    def test_no_vehicles_need_electrification(self, mock_should_electrify):
        mock_should_electrify.side_effect = [False, False]
        result = n_vehicles_to_electrify(self.vehicles)
        assert result == 0

    def test_mixed_vehicles_need_electrification(self, mock_should_electrify):
        mock_should_electrify.side_effect = [True, False]
        result = n_vehicles_to_electrify(self.vehicles)
        assert result == 1

    def test_empty_vehicle_list(self, mock_should_electrify):
        result = n_vehicles_to_electrify([])
        mock_should_electrify.assert_not_called()
        assert result == 0

    def test_single_vehicle_need_electrification(self, mock_should_electrify):
        mock_should_electrify.side_effect = [True]
        result = n_vehicles_to_electrify([self.mock_vehicle1])
        assert result == 1

    def test_single_vehicle_no_need_electrification(self, mock_should_electrify):
        mock_should_electrify.side_effect = [False]
        result = n_vehicles_to_electrify([self.mock_vehicle1])
        assert result == 0
