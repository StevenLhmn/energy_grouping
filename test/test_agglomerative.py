import unittest
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from src.grouping.agglomerative import Agglomerative
from src.data_gen.region_generator import RegionGenerator


class Test_BruteForce(unittest.TestCase):

    def test_smallest(self):
        agg = Agglomerative(1, max_clusters=2)

        id_smallest = agg._smallest(
            pd.DataFrame(
                np.array([
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]),
                columns= ["a", "b", "c"]
            )
        )
        self.assertEqual(id_smallest, 0)


if __name__ == '__main__':
    unittest.main()