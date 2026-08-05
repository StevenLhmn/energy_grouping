import unittest
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import date
from shapely.geometry import Point, Polygon
from src.grouping.brute_force import Brute_Force
from src.data_gen.lpg_wrapper import LPG_Wrapper


class Test_BruteForce(unittest.TestCase):

    def test_positive(self):
        dict = {
            "a": (1,2),
            "b": (2,3),
            "c": (3,1)
        }
        lable_dict = Brute_Force().group(dict, )
        aimed_result = {
            "a": 1,
            "b": 1,
            "c": 2
        }
        self.assertTrue()

    def test_powerset(self):
        set = {1, 2, 3}
        result = Brute_Force()._powerset(set)
        aimed_result = [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
        self.assertEqual(result, aimed_result)

    def test_partitions(self):
        set = {1, 2, 3}
        result = Brute_Force()._partitions(set)
        aimed_result = [[{1}, {2}, {3}], [{1, 2}, {3}], [{1, 3}, {2}], [{2, 3}, {1}], [{1, 2, 3}]]
        self.assertEqual(result, aimed_result)

    def test_bell_number(self):
        aimed_result = [1, 1, 2, 5, 15, 52]
        for n in range(6):
            set = np.arange(n)
            result = Brute_Force()._partitions(set)
            self.assertEqual(len(result), aimed_result[n])

if __name__ == '__main__':
    unittest.main()