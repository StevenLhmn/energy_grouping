from src.data.region import Region
import numpy as np

class GroupedRegion:
    def __init__(self, region: Region, labels: map[str: int]):
        
        self.region = region
        self.labels = self._check_labels(labels)

    def _check_labels(self, labels: map[str: int]):
        #TODO: check if labels are valid 
        #not empty
        #keys unique
        #non negative lables
        #all ids in region
        #all ids have a lable
        return labels

    def get_region_autarky(self, ):
        pass

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
            raise Exception(f'"gen is not a 1d or 2d array. shape is {gen.shape}')
        
        if total_load == 0:
            return 0
        elif total_load < 0:
            raise Exception("total load is negative")
        elif total_load > 0:
            return self_consumption / total_load

    def region_autarky(self):
        houses = self.region.houses.copy()
        houses = houses["label"] = houses["id"].map(self.labels)
        ids = list(self.labels.keys())
        houses = houses[houses["id"].isin(ids)]
        
        # def optimization_function(self, grouped_region: GroupedRegion, distance_factor: float):
        #     """
        #     Calculates the autarky of a grouped region and returns the negative value of it.
        #     This is used as an optimization function for the grouping algorithm.
        #     The distance factor is used to penalize groups that are too far apart.
        #     """
        #     gen = grouped_region.get_gen()
        #     load = grouped_region.get_load()
        #     autarky = self.get_autarky(gen, load)
        #     distance_penalty = distance_factor * grouped_region.get_average_distance()
        #     return -autarky + distance_penalty