from savings.energy.scale_energy_by_occupancy import scale_energy_by_occupancy


class TestScaleEnergyByOccupancy:
    def test_it_returns_same_if_occupancy_is_none(self):
        assert scale_energy_by_occupancy(10) == 10

    def test_it_scales_proportionally(self):
        # Not technically allowed as occupancy_int should be an int, but just to test the maths
        assert scale_energy_by_occupancy(10, 5.4) == 20

        assert scale_energy_by_occupancy(10, 4) == 10 * 4 / 2.7
        assert scale_energy_by_occupancy(10, 1) == 10 * 1 / 2.7
