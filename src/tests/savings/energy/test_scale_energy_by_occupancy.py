from savings.energy.scale_energy_by_occupancy import scale_energy_by_occupancy


class TestScaleEnergyByOccupancy:
    def test_it_returns_same_if_occupancy_is_none(self):
        assert scale_energy_by_occupancy(10) == 10

    def test_it_scales_nonlinearly_using_multiplier(self):
        assert scale_energy_by_occupancy(10, 4) == 10 * 1.07
        assert scale_energy_by_occupancy(10, 1) == 10 * 0.56

    def test_it_caps_at_5(self):
        assert scale_energy_by_occupancy(10, 5) == scale_energy_by_occupancy(10, 6)
        assert scale_energy_by_occupancy(10, 5) == scale_energy_by_occupancy(10, 100)
        assert scale_energy_by_occupancy(10, 5) == 10 * 1.37
