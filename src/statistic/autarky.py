import pandas as pd
import numpy as np
from src.data.grouped_region import GroupedRegion

class Autarky:
    def _check_same_shape(self, arr1, arr2):
        if arr1.shape != arr2.shape:
            raise Exception("shapes of list1 and list2 do not match")

    def _sum_by_element(self, arr):
        result = np.sum(arr, axis=0)
        return result

    def group_self_consumption(self, gen: np.ndarray, load: np.ndarray):
        """
        calculates the max amount of selfconsumption where all houses are fully connected.
        if gen or load are a list of lists then the the sum of them will be used
        gen: list of floats (list of houses with each having a timeseries)
        load: list of floats (list of houses with each having a timeseries)
        """
        self._check_same_shape(gen, load)
        if len(gen.shape) == 1:
            gen_sum = gen
            load_sum = load 
        elif len(gen.shape) == 2:
            gen_sum = self._sum_by_element(gen)
            load_sum = self._sum_by_element(load)
        else:
            raise Exception(f'gen is not a 1d or 2d array. shape is {gen.shape}')
        
        self_consumption = np.minimum(gen_sum, load_sum)
        return self_consumption

    def get_autarky(self, gen: np.ndarray, load: np.ndarray):
        self_consumption = sum(self.group_self_consumption(gen, load))
        if len(load.shape) == 1:
            total_load = sum(load)
        elif len(load.shape) == 2:
            total_load = sum(self._sum_by_element(load))
        else:
            raise Exception(f'"en is not a 1d or 2d array. shape is {gen.shape}')
        
        if total_load == 0:
            return 0
        elif total_load < 0:
            raise Exception("total load is negative")
        elif total_load > 0:
            return self_consumption / total_load

    def optimization_function(self, grouped_region: GroupedRegion, distance_factor: float):

