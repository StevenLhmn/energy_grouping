from src.data.region import Region
import numpy as np

class GroupedRegion:
    def __init__(self, region: Region, labels: dict[str: int]):
        
        self.region = region
        self.labels = self._check_labels(labels)

    def _check_labels(self, labels: dict[str: int]):
        #TODO: check if labels are valid 
        #not empty
        #keys unique
        #non negative lables
        #all ids in region
        #all ids have a lable
        return labels

    @staticmethod
    def _check_same_shape(arr1, arr2):
        if not isinstance(arr1, np.ndarray) or not isinstance(arr2, np.ndarray):
            raise TypeError("arr1 and arr2 must be numpy arrays")
        if arr1.shape != arr2.shape:
            raise ValueError("shapes of list1 and list2 do not match")
        
    @staticmethod
    def _sum_by_element(arr):
        result = np.sum(arr, axis=0)
        return result
    
    @staticmethod
    def group_self_consumption(gen: np.ndarray, load: np.ndarray):
        """
        calculates the max amount of selfconsumption where all houses are fully connected.
        if gen or load are a list of lists then the the sum of them will be used
        gen: 2d np.array (list of houses with each having a timeseries)
        load: 2d np.array (list of houses with each having a timeseries)
        """
        GroupedRegion._check_same_shape(gen, load)
        if len(gen.shape) == 1:
            gen_sum = gen
            load_sum = load 
        elif len(gen.shape) == 2:
            gen_sum = GroupedRegion._sum_by_element(gen)
            load_sum = GroupedRegion._sum_by_element(load)
        else:
            raise ValueError(f'gen is not a 1d or 2d array. shape is {gen.shape}')
        if np.any(gen_sum < 0) or np.any(load_sum < 0):
            raise ValueError("gen or load contain negative values")
        
        self_consumption = np.minimum(gen_sum, load_sum)
        return self_consumption
    
    def get_autarky(self, gen: np.ndarray, load: np.ndarray):
        self_consumption = sum(self.group_self_consumption(gen, load))
        if len(load.shape) == 1:
            total_load = sum(load)
        elif len(load.shape) == 2:
            total_load = sum(GroupedRegion._sum_by_element(load))
        else:
            raise Exception(f'"gen is not a 1d or 2d array. shape is {gen.shape}')
        
        if total_load == 0:
            return 0
        elif total_load < 0:
            raise Exception("total load is negative")
        elif total_load > 0:
            return self_consumption / total_load

    def region_autarky(self):
        """
        calculates the autarky of the region based on the labels
        
        return: the total autarky of the region
        """
        houses = self.region.houses.copy()
        houses["label"] = houses["id"].map(self.labels)
        total_self_consumption = 0
        for label in houses["label"].unique():
            group = houses[houses["label"] == label]
            gen = np.array(group["gen"].tolist())
            load = np.array(group["load"].tolist())
            self_consumption = self.group_self_consumption(gen, load)
            total_self_consumption += self_consumption.sum()

        return total_self_consumption / np.array(houses["load"].to_list()).sum()

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