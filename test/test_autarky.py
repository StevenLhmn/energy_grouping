import unittest
import numpy as np
import pandas as pd
from src.statistic.autarky import Autarky


class Test_Autarky(unittest.TestCase):

    def test_single_house(self):
        load = np.array([1, 2, 3])
        gen = np.array([3, 2, 1])
        self_cons = Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))
        self.assertEqual(self_cons.shape[0], 3)
        self.assertEqual(self_cons, np.array([1, 2, 1]))

    def test_multiple_houses(self):
        load1 = np.array([1, 2, 3])
        gen1 = np.array([3, 2, 1])
        load2 = np.array([2, 3, 4])
        gen2 = np.array([4, 3, 2])
        self_cons = Autarky().group_self_consumption(pd.DataFrame({'load': [load1, load2], 'gen': [gen1, gen2]}))
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.allclose(self_cons, np.array([3, 5, 5])))

    def test_zero_generation(self):
        load = np.array([1, 2, 3])
        gen = np.array([0, 0, 0])
        self_cons = Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.allclose(self_cons, np.array([0, 0, 0])))

    def test_zero_load(self):
        load = np.array([0, 0, 0])
        gen = np.array([1, 2, 3])
        self_cons = Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))
        self.assertEqual(self_cons.shape[0], 3)
        self.assertTrue(np.allclose(self_cons, np.array([1, 2, 3])))

    def test_mismatched_lengths(self):
        load = np.array([1, 2])
        gen = np.array([3, 2, 1])
        with self.assertRaises(ValueError):
            Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))

    def test_empty_arrays(self):
        load = np.array([])
        gen = np.array([])
        self_cons = Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))
        self.assertEqual(self_cons.shape[0], 0)
        self.assertTrue(np.allclose(self_cons, np.array([])))

    def test_large_arrays(self):
        load = np.random.rand(1000)
        gen = np.random.rand(1000)
        self_cons = Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))
        self.assertEqual(self_cons.shape[0], 1000)
        self.assertTrue(np.all(self_cons <= load + gen))

    def test_negative_values(self):
        load = np.array([-1, -2, -3])
        gen = np.array([-3, -2, -1])
        with self.assertRaises(ValueError):
            Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))

    def test_non_numpy_arrays(self):
        load = [1, 2, 3]
        gen = [3, 2, 1]
        with self.assertRaises(TypeError):
            Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))

    def test_non_numeric_values(self):
        load = np.array([1, 2, 'a'])
        gen = np.array([3, 2, 1])
        with self.assertRaises(TypeError):
            Autarky().group_self_consumption(pd.DataFrame({'load': [load], 'gen': [gen]}))


if __name__ == '__main__':
    unittest.main()
