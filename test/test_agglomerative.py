import unittest
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from src.grouping.agglomerative import Agglomerative
from src.data_gen.region_generator import RegionGenerator


class Test_Agglomerative(unittest.TestCase):

    def setUp(self):
        self.agg = Agglomerative(1, max_clusters=2)

    def test_check_matrix_rejects_non_dataframe(self):
        with self.assertRaises(TypeError):
            self.agg._get_id_smallest_in_triangle([[0, 1],
                                    [1, 0]])

    def test_check_matrix_rejects_non_square_dataframe(self):
        with self.assertRaises(ValueError):
            self.agg._get_id_smallest_in_triangle(pd.DataFrame([[0, 1, 2],
                                                 [1, 0, 3]]))

    def test_check_matrix_rejects_non_finite_values(self):
        with self.assertRaises(ValueError):
            self.agg._get_id_smallest_in_triangle(pd.DataFrame([[0, np.nan],
                                                 [1, 0]]))

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


if __name__ == '__main__':
    unittest.main()