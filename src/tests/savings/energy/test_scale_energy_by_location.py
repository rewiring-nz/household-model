from openapi_client.models.cooktop_enum import CooktopEnum
from openapi_client.models.location_enum import LocationEnum
from openapi_client.models.space_heating_enum import SpaceHeatingEnum
from openapi_client.models.water_heating_enum import WaterHeatingEnum
from savings.energy.scale_energy_by_location import scale_energy_by_location


class TestScaleEnergyByLocation:
    def test_it_returns_same_if_machine_type_is_not_space_heating(self):
        assert (
            scale_energy_by_location(CooktopEnum.GAS, 10, LocationEnum.AUCKLAND_CENTRAL)
            == 10
        )
        assert (
            scale_energy_by_location(
                WaterHeatingEnum.GAS, 10, LocationEnum.AUCKLAND_CENTRAL
            )
            == 10
        )

    def test_it_returns_same_if_location_is_none(self):
        assert scale_energy_by_location(SpaceHeatingEnum.GAS, 10) == 10

    def test_it_returns_same_if_location_is_missing(self):
        assert scale_energy_by_location(SpaceHeatingEnum.GAS, 10, "BLAH") == 10

    def test_it_scales_space_heating(self):
        assert (
            scale_energy_by_location(SpaceHeatingEnum.GAS, 10, LocationEnum.NORTHLAND)
            == 4.938220361
        )
        assert (
            scale_energy_by_location(SpaceHeatingEnum.GAS, 10, LocationEnum.OTAGO)
            == 16.01023022
        )
