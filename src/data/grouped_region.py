import numpy as np
import pandas as pd
from src.data.region import Region

class GroupedRegion:


    def __init__(self, region: Region, labels: dict[str: int]):
        
        self.houses = region.houses.copy()
        self.houses["label"] = self.houses["id"].map(self._check_labels(labels))

    def _check_labels(self, labels: dict[str: int]):
        if labels is None:
            raise ValueError(f'Labels is None')
        if not isinstance(labels, dict):
            raise ValueError(f'labels in not a dict') 
        #TODO: check if labels are valid 
        #not empty
        #keys unique
        #non negative lables
        #all ids in region
        #all ids have a lable
        return labels

    @staticmethod
    def _check_weight(weight: float):
        if not 0 <= weight <= 1:
            raise ValueError("weight must be between 0 and 1")
        return weight

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
    
    def group_autarky(self, gen: np.ndarray, load: np.ndarray):
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
        
        return: the total autarky of the region in decimal from 0 to 1
        """
        houses = self.houses.copy()
        total_self_consumption = 0
        for label in houses["label"].unique():
            group = houses[houses["label"] == label]
            gen = np.array(group["gen"].tolist())
            load = np.array(group["load"].tolist())
            self_consumption = self.group_self_consumption(gen, load)
            total_self_consumption += self_consumption.sum()

        return total_self_consumption / np.array(houses["load"].to_list()).sum()

    def region_distance_score(self):
        """
        returns the relation of the euclidean distance between all houses and the center in realtion to all houses and its groups centers

        return: the total distance score of the region in decimal from 0 to 1
        """
        houses = self.houses.copy()
        if houses.crs != "EPSG:3857":
            houses = houses.to_crs("EPSG:3857")
       
        centroid = houses.geometry.union_all().centroid
        
        distance = houses.geometry.distance(centroid).sum()
        group_distance = 0

        for label in houses["label"].unique():
            group = houses[houses["label"] == label]
            group_centroid = group.geometry.union_all().centroid
            group_distance += group.geometry.distance(group_centroid).sum()

        return 1 - (group_distance / distance) if distance > 0 else 1

    def region_score(self, distance_weight: float = 0.5):
        """
        mixes autarky with distance to find the best grouping.
        
        return: the total score of the region
        """
        if not 0 <= distance_weight <= 1:
            raise ValueError("distance_weight must be between 0 and 1")

        autarky = self.region_autarky() * (1 - distance_weight)
        distance = self.region_distance_score() * distance_weight
        return autarky + distance

    def get_labels(self):
        labels = self.houses[["id","label"]]
        return labels.set_index("id")["label"].to_dict()

    def get_partition(self):
        partition = {}
        for label in self.houses["label"].unique():
            group = self.houses[self.houses["label"] == label]
            partition[label] = frozenset(group["id"].tolist())
        return frozenset(partition.values())

    def get_group_centroids(self):
        centroids = pd.DataFrame(columns=["x", "y", "label", ])
        for label in self.houses["label"].unique():
            group = self.houses[self.houses["label"] == label]
            centroid = group.geometry.union_all().centroid
            centroids = pd.concat([centroids, pd.DataFrame({"x": [centroid.x], "y": [centroid.y], "label": [label]})], ignore_index=True)
        return centroids

    def get_autarky_without_groups(self):
        self_cons = 0
        load = 0
        for _, row in self.houses.iterrows():
            self_cons += self.group_self_consumption(row["gen"], row["load"]).sum()
            load += row["load"].sum()
        autarky = self_cons/load if load > 0 else 1
        return autarky