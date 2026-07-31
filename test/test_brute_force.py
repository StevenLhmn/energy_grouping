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

if __name__ == '__main__':
    unittest.main()