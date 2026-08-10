import numpy as np
import matplotlib.pyplot as plt
from src.grouping.i_grouping_algo import I_Grouping_Algo
from itertools import combinations
from collections.abc import Callable 
from src.data.region import Region
from src.statistic.autarky import Autarky
from src.data.grouped_region import GroupedRegion


class Brute_Force(I_Grouping_Algo):

    def _powerset(self, set : set):
        powerset = [
                    subset
                    for len in range(len(set) + 1)
                    for subset in combinations(set, len)
                ]
        return powerset

    def _partitions(self, set):
        if not set:
            return [[]]

        elements = list(set)
        first = elements[0]
        rest = set(elements[1:])

        result = []

        for partition in self._partitions(rest):
            # Put first into each existing block
            for i in range(len(partition)):
                new_partition = [block[:] for block in partition]
                new_partition[i].append(first)
                result.append(new_partition)

            # Put first into its own new block
            result.append([[first]] + partition)

        return result

    def group(self, region: Region) -> GroupedRegion:
        """
        vector_dict: {id -> vector, ...}
        vector: (dim1, dim2, ...)
        dimX: float 

        return: {id -> lable, ...}
        """
        # 1. find all unique group combinations (power sert).
        combinations = self._powerset(set(region.get_indexes()))

        # 2. calculate group loads and selfcons. TODO check if its faster
        # houses = region.houses
        # autarky = Autarky()
        # self_consumption = {}
        # for combination in combinations:
        #     gen_load = houses.loc[houses["id"].isin(combination), ["load", "gen"]]
        #     self_consumption[combination] = autarky.group_self_consumption(gen_load)

        # 3. find all partitions of the region
        partitions = self._partitions(set(region.get_indexes()))

        #4. calculate the autarky for each partition and find the best one
        best_partition = None
        for partition in partitions:
            partition_autarky = 0
            labels = {}
            for label, group in enumerate(partition):
                for id in group:
                    labels[id] = label
                    region = GroupedRegion(region, labels=labels)
                    region.
            if best_partition is None or partition_autarky > best_partition[1]:
                best_partition = (partition, partition_autarky)


    def animate(self, ax :plt.Axes):
        """Show an animatoin of the algo"""
        pass
        