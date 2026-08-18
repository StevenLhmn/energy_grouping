import unittest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from src.grouping.brute_force import Brute_Force
from src.data_gen.region_generator import RegionGenerator


class Test_BruteForce(unittest.TestCase):

    def test_powerset(self):
        set = {1, 2, 3}
        result = Brute_Force()._powerset(set)
        aimed_result = [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
        self.assertEqual(result, aimed_result)

    def test_partitions(self):
            fs = frozenset
            input = {1, 2, 3}
            result = Brute_Force()._partitions(input)
            aimed_result = {
                fs({fs({1}), fs({2}), fs({3})}),
                fs({fs({1, 2}), fs({3})}),
                fs({fs({1, 3}), fs({2})}),
                fs({fs({2, 3}), fs({1})}),
                fs({fs({1, 2, 3})})
            }
            self.assertEqual(result, aimed_result)

    def test_bell_number(self):
        aimed_result = [1, 1, 2, 5, 15, 52]
        for n in range(6):
            set = np.arange(n)
            result = Brute_Force()._partitions(set)
            self.assertEqual(len(result), aimed_result[n])

    def test_positive(self):
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
        grouped_region = Brute_Force().group(RegionGenerator().simple_from_gdf(gdf))
        aimed_result = {
            "X0.000000|Y0.000000": 0,
            "X1.000000|Y1.000000": 0,
            "X2.000000|Y2.000000": 0
        }
        self.assertEqual(grouped_region.labels, aimed_result)

    def test_positive(self):
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
        grouped_region, score = Brute_Force().group(region, .5)
        aimed_result = frozenset([
            frozenset(["X0.000000|Y0.000000"]),
            frozenset(["X1.000000|Y1.000000"]),
            frozenset(["X2.000000|Y2.000000"])
        ])
        partition = grouped_region.get_partition()
        self.assertEqual(partition, aimed_result)
        self.assertAlmostEqual(score, 0.9666, places=3)

    def test_small_weight(self):
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
        grouped_region, score = Brute_Force().group(region, .1)
        aimed_result = frozenset([
            frozenset(["X0.000000|Y0.000000"]),
            frozenset(["X1.000000|Y1.000000", "X2.000000|Y2.000000"])
        ])
        partition = grouped_region.get_partition()
        self.assertEqual(partition, aimed_result)
        self.assertAlmostEqual(score, 0.9500, places=3)

    def test_triangle(self):
        gdf = gpd.GeoDataFrame(
            {
                "coordinate": [
                    Point(1, 1),
                    Point(3, 3),
                    Point(3, 1),
                ],
                "gen": [
                        np.array([0]),
                        np.array([3]),
                        np.array([1]),
                    ],
                "load": [
                    np.array([3]),
                    np.array([0]),
                    np.array([1]),
                ]   
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )
        region = RegionGenerator().simple_from_gdf(gdf)
        grouped_region, score = Brute_Force().group(region, .5)
        aimed_result = frozenset([
            frozenset({'X1.000000|Y1.000000', 'X3.000000|Y3.000000'}),
            frozenset(["X3.000000|Y1.000000"])
        ])
        partition = grouped_region.get_partition()
        self.assertEqual(partition, aimed_result)
        self.assertAlmostEqual(score, 0.6396, places=3)

    def test_zero(self):
        gdf = gpd.GeoDataFrame(
            {
                "coordinate": [
                    Point(1, 1),
                    Point(3, 3),
                    Point(3, 1),
                ],
                "gen": [
                        np.array([0]),
                        np.array([0]),
                        np.array([0]),
                    ],
                "load": [
                    np.array([1]),
                    np.array([1]),
                    np.array([0]),
                ]   
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )
        region = RegionGenerator().simple_from_gdf(gdf)
        grouped_region, score = Brute_Force().group(region, .5)
        aimed_result = frozenset([
            frozenset(["X1.000000|Y1.000000"]),
            frozenset(["X3.000000|Y1.000000"]),
            frozenset(["X3.000000|Y3.000000"])
        ])
        partition = grouped_region.get_partition()
        self.assertEqual(partition, aimed_result)
        self.assertAlmostEqual(score, 0.5000, places=3)


if __name__ == '__main__':
    unittest.main()