import unittest
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import date
from shapely.geometry import Point, Polygon
from src.data.region import Region
from src.data_gen.lpg_wrapper import LPG_Wrapper


class Test_LPGWrapper(unittest.TestCase):

    def test_seed_is_set(self):
        seed = 42
        lpg = LPG_Wrapper(seed)
        # Check if the seed is set correctly
        self.assertEqual(lpg.seed, seed)

    def test_seed_is_negative(self):
        with self.assertRaises(ValueError):
            LPG_Wrapper(seed=-1)

    def test_seed_is_above_limit(self):
        with self.assertRaises(ValueError):
            LPG_Wrapper(seed=2**33)

    def test_seed_is_none(self):
        with self.assertRaises(ValueError):
            LPG_Wrapper(seed=None)

    # can take a long time ~5-10mins
    def test_generate_appartment(self):
        for _ in range(10):
            lpg = LPG_Wrapper(42)
            load = lpg.generate_appartment(2, date(2022, 4, 1), date(2022, 4, 1), "1h")
            self.assertEqual(len(load), 24)

    def test_generate_appartment_zero(self):
        lpg = LPG_Wrapper(42)
        load = lpg.generate_appartment(0, date(2022, 4, 1), date(2022, 4, 1), "1h")
        # has to be a nparray and 24 slots long
        self.assertIsInstance(load, np.ndarray) 
        self.assertEqual(len(load), 24)

    def test_generate_appartment_too_high(self):
        lpg = LPG_Wrapper(42)
        with self.assertRaises(ValueError):
            lpg.generate_appartment(101, date(2022, 4, 1), date(2022, 4, 1), "1h")

    def test_generate_appartment_date_format_invalid(self):
        lpg = LPG_Wrapper(42)
        with self.assertRaises(ValueError):
            lpg.generate_appartment(101, '2022.04.01', '2022.04.01', "1h")

    def test_generate_appartment_start_after_end(self):
        lpg = LPG_Wrapper(42)
        with self.assertRaises(ValueError):
            lpg.generate_appartment(101, date(2022, 4, 1), date(2022, 4, 1), "1h")
        
    def test_generate_appartment_interval_invalid(self):
        lpg = LPG_Wrapper(42)
        with self.assertRaises(ValueError):
            lpg.generate_appartment(101, date(2022, 4, 1), date(2022, 4, 1), "2h")


if __name__ == '__main__':
    unittest.main()