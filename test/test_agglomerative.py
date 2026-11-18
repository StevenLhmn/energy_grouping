import unittest
import numpy as np
import geopandas as gpd
import pandas as pd
from src.data.region import Region
from shapely.geometry import Point
from src.grouping.agglomerative import Agglomerative
from src.data_gen.region_generator import RegionGenerator


class Test_Agglomerative(unittest.TestCase):

    def setUp(self):
        self.agg = Agglomerative(1, max_clusters=2)

    def test_check_matrix_rejects_non_dataframe(self):
        with self.assertRaises(TypeError):
            self.agg._get_id_smallest_in_triangle([
                [0, 1],
                [1, 0]
            ])

    def test_check_matrix_rejects_non_square_dataframe(self):
        with self.assertRaises(ValueError):
            self.agg._get_id_smallest_in_triangle(pd.DataFrame([
                [0, 1, 2],
                [1, 0, 3]
            ]))

    def test_check_matrix_rejects_non_finite_values(self):
        with self.assertRaises(ValueError):
            self.agg._get_id_smallest_in_triangle(pd.DataFrame([
                [0, np.nan],
                [1, 0]
            ]))

    def test_get_id_smallest_in_triangle(self):
        row, collumn = self.agg._get_id_smallest_in_triangle(
            pd.DataFrame(
                np.array([
                    [0, 4, 3],
                    [1, 0, 2],
                    [2, 5, 0]
                ]),
                columns= ["a", "b", "c"]
            )
        )
        self.assertEqual(row, 1)
        self.assertEqual(collumn, "c") 

    def test_get_id_smallest_in_triangle_small_matrix(self):
        row, collumn = self.agg._get_id_smallest_in_triangle(
            pd.DataFrame(
                np.array([
                    [0, 2],
                    [1, 0],
                ]),
                columns=["a", "b"]
            )
        )
        self.assertEqual(row, 0)
        self.assertEqual(collumn, "b")

    def test_get_id_smallest_in_triangle_same_smallest(self):
            row, collumn = self.agg._get_id_smallest_in_triangle(
                pd.DataFrame(
                    np.array([
                        [0, 2, 2],
                        [1, 0, 2],
                        [2, 5, 0]
                    ]),
                    columns=["a", "b", "c"]
                )
            )
            # has to always choose the top rigth one
            self.assertEqual(row, 0)
            self.assertEqual(collumn, "b")

    def test_group(self):
        gdf = gpd.GeoDataFrame({
                'gen': [
                    np.array([10, 5]),
                    np.array([2, 6]),
                    np.array([5, 20]),
                    np.array([3, 25]),
                    np.array([0, 5])],
                'load': [
                    np.array([5, 10]),
                    np.array([8, 0]),
                    np.array([3, 25]),
                    np.array([5, 22]),
                    np.array([0, 3])],
                'coordinate': [
                    Point(1, 1),
                    Point(2, 2),
                    Point(3, 3),
                    Point(4, 4),
                    Point(5, 5)]
                },
            geometry='coordinate',
            crs="EPSG:3857"
        )
        region = Region(gdf)
        grouped_region = Agglomerative(0, 2).group(region)
        expected = {
            "X1.000000|Y1.000000": 1,
            "X2.000000|Y2.000000": 1,
            "X3.000000|Y3.000000": 2,
            "X4.000000|Y4.000000": 2,
            "X5.000000|Y5.000000": 2,        }
        self._assert_same_grouped_region_labels(grouped_region.get_labels(), expected)


    def _assert_same_grouped_region_labels(self, result, target):
        result_groups = {
            frozenset(house_id for house_id, label in result.items() if label == group_label)
            for group_label in set(result.values())
        }
        target_groups = {
            frozenset(house_id for house_id, label in target.items() if label == group_label)
            for group_label in set(target.values())
        }
        if result_groups != target_groups:
            raise AssertionError(
                f'target groups: {target_groups}, result groups: {result_groups}'
            )


if __name__ == '__main__':
    unittest.main()