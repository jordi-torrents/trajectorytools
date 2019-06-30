import pathlib
import unittest

import numpy as np
import numpy.testing as nptest
from trajectorytools import Trajectories
from trajectorytools.constants import dir_of_data

trajectories_path = pathlib.Path(dir_of_data) / 'test_trajectories_idtrackerai.npy'
raw_trajectories_path = pathlib.Path(dir_of_data) / 'test_trajectories.npy'

class TrajectoriesTestCase(unittest.TestCase):
    def setUp(self):
        self.t = Trajectories.from_idtracker(trajectories_path)

    def test_center_of_mass(self):
        nptest.assert_equal(self.t.s.mean(axis=1), self.t.center_of_mass.s)
        nptest.assert_equal(self.t.v.mean(axis=1), self.t.center_of_mass.v)
        nptest.assert_equal(self.t.a.mean(axis=1), self.t.center_of_mass.a)

    def test_check_unit_change(self, new_length_unit=10, new_time_unit=3):
        length_unit = self.t.params['length_unit']
        time_unit = self.t.params['time_unit']

        s, v, a = self.t.s, self.t.v, self.t.a

        factor_length = new_length_unit / length_unit
        factor_time = new_time_unit / time_unit

        self.t.new_length_unit(new_length_unit)
        nptest.assert_allclose(self.t.s, s/factor_length)
        nptest.assert_allclose(self.t.v, v/factor_length)
        nptest.assert_allclose(self.t.a, a/factor_length)

        self.t.new_time_unit(new_time_unit)
        nptest.assert_allclose(self.t.s, s/factor_length)
        nptest.assert_allclose(self.t.v, v/factor_length * factor_time)
        nptest.assert_allclose(self.t.a, a/factor_length * factor_time**2)

    def test_slice(self):
        new_t = self.t[50:100]
        assert(isinstance(new_t, Trajectories))
        self.assertEqual(new_t.number_of_individuals,
                         self.t.number_of_individuals)
        nptest.assert_equal(new_t.s, self.t.s[50:100])
        nptest.assert_equal(new_t.v, self.t.v[50:100])
        nptest.assert_equal(new_t.a, self.t.a[50:100])

class RawTrajectoriesTestCase(TrajectoriesTestCase):
    def setUp(self):
        t = np.load(raw_trajectories_path, allow_pickle=True)
        self.t = Trajectories.from_positions(t)

class TrajectoriesRadiusTestCase(TrajectoriesTestCase):
    def setUp(self):
        self.t_normal = Trajectories.from_idtracker(trajectories_path,
                                                    smooth_sigma=1)
        self.t = Trajectories.from_idtracker(trajectories_path,
                                             smooth_sigma=1,
                                             normalise_by='radius')
    def test_scaling(self):
        self.assertEqual(self.t.params['radius'], 1.0)
        nptest.assert_allclose(self.t.v,
                               self.t_normal.v / self.t.params['radius_px'])
        nptest.assert_allclose(self.t.a,
                               self.t_normal.a / self.t.params['radius_px'],
                               atol=1e-12)

if __name__ == '__main__':
    unittest.main()