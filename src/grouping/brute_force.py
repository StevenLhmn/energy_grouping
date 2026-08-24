import matplotlib.pyplot as plt
from itertools import combinations
from src.data.region import Region
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo


class Brute_Force(GroupingAlgo):

    def __init__(self, distance_weight: float):
        self.distance_weight = GroupedRegion._check_weight(distance_weight)

    def __str__(self):
            return "Brute Force"

    def _powerset(self, set : set):
        powerset = [
                    subset
                    for len in range(len(set) + 1)
                    for subset in combinations(set, len)
                ]
        return powerset

    def _partitions(self, s: set):
        if len(s) <= 0:
            return [frozenset()]

        elements = list(s)
        first = elements[0]
        rest = set(elements[1:])

        result = set()

        for partition in self._partitions(rest):
            # Put first into each existing block
            for i, block in enumerate(partition):
                new_partition = list(partition)
                new_partition[i] = block | frozenset([first])
                result.add(frozenset(new_partition))

            # Put first into a new block
            result.add(partition | frozenset([frozenset([first])]))

        return result

    def group(self, region: Region) -> GroupedRegion:
        """
        vector_dict: {id -> vector, ...}
        vector: (dim1, dim2, ...)
        dimX: float 

        return: {id -> lable, ...}
        """
        # 1. find all unique group combinations (power set).
        # combinations = self._powerset(set(region.get_indexes()))

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
            grouped_region = GroupedRegion(region, labels=labels)
            partition_score = grouped_region.region_score(self.distance_weight)
            if best_partition is None or partition_score > best_partition[0]:
                best_partition = (partition_score, labels)
        
        return (
            GroupedRegion(region, labels=best_partition[1]),
            f'(Partitions: {len(partitions)})',
        )


    def animate(self, ax :plt.Axes):
        """Show an animatoin of the algo"""
        pass
        