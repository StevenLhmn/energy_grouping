import unittest
import numpy as np
import pandas as pd
from src.data.grouped_region import GroupedRegion
from src.data_gen.region_generator import RegionGenerator
import geopandas as gpd
from shapely.geometry import Point


class Test_GroupedRegion(unittest.TestCase):

    def test_grouped_region(self):
        load = np.array([1, 2, 3])
        gen = np.array([3, 2, 1])
        self_cons = GroupedRegion.group_self_consumption(gen=gen, load=load)
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.array_equal(self_cons, np.array([1, 2, 1])))

    def test_multiple_houses(self):
        load1 = np.array([1, 2, 3])
        gen1 = np.array([3, 2, 1])
        load2 = np.array([2, 3, 4])
        gen2 = np.array([4, 3, 2])
        load = np.array([load1, load2])
        gen = np.array([gen1, gen2])
        self_cons = GroupedRegion.group_self_consumption(load=load, gen=gen)
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.allclose(self_cons, np.array([3, 5, 3])))

    def test_zero_generation(self):
        load = np.array([1, 2, 3])
        gen = np.array([0, 0, 0])
        self_cons = GroupedRegion.group_self_consumption(gen=gen, load=load)
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.allclose(self_cons, np.array([0, 0, 0])))

    def test_zero_load(self):
        load = np.array([0, 0, 0])
        gen = np.array([1, 2, 3])
        self_cons = GroupedRegion.group_self_consumption(gen=gen, load=load)
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.allclose(self_cons, np.array([0, 0, 0])))

    def test_mismatched_lengths(self):
        load = np.array([1, 2])
        gen = np.array([3, 2, 1])
        with self.assertRaises(ValueError):
            GroupedRegion.group_self_consumption(gen=gen, load=load)

    def test_empty_arrays(self):
        load = np.array([])
        gen = np.array([])
        self_cons = GroupedRegion.group_self_consumption(gen=gen, load=load)
        self.assertEqual(self_cons.shape[0], 0)
        self.assertTrue(np.allclose(self_cons, np.array([])))

    def test_large_arrays(self):
        load = np.random.rand(1000)
        gen = np.random.rand(1000)
        self_cons = GroupedRegion.group_self_consumption(gen=gen, load=load)
        self.assertEqual(self_cons.shape[0], 1000)
        self.assertTrue(np.all(self_cons <= load + gen))

    def test_negative_values(self):
        load = np.array([-1, -2, -3])
        gen = np.array([-3, -2, -1])
        with self.assertRaises(ValueError):
            GroupedRegion.group_self_consumption(gen=gen, load=load)

    def test_non_numpy_arrays(self):
        load = [1, 2, 3]
        gen = [3, 2, 1]
        with self.assertRaises(TypeError):
            GroupedRegion.group_self_consumption(gen=gen, load=load)

    def test_non_numeric_values(self):
        load = np.array([1, 2, 'a'])
        gen = np.array([3, 2, 1])
        with self.assertRaises(TypeError):
            GroupedRegion.group_self_consumption(gen=gen, load=load)

    def test_region_autarky(self):
        gdf = gpd.GeoDataFrame(
            {
                "coordinate": [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2),
                ],
                "load": [
                        np.array([1,1,1]),
                        np.array([2,3,1]),
                        np.array([1,2,3]),
                    ],
                "gen": [
                    np.array([3,1,2]),
                    np.array([2,2,1]),
                    np.array([1,3,3]),
                ]   
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )
        region = RegionGenerator().simple_from_gdf(gdf)
        labels = {
            "X0.000000|Y0.000000": 1,
            "X1.000000|Y1.000000": 2,
            "X2.000000|Y2.000000": 2
        }
        grouped_region = GroupedRegion(region, labels=labels)
        autarky = grouped_region.region_autarky()
        self.assertAlmostEqual(autarky, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
