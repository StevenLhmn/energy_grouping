import matplotlib.pyplot as plt
from src.grouping.i_grouping_algo import I_Grouping_Algo
from itertools import combinations
from collections.abc import Callable 
from src.data.region import Region
from src.statistic.autarky import Autarky


class Brute_Force(I_Grouping_Algo):

    def group(self, region: Region, opti_func: Callable[]) -> None:
        """
        vector_dict: {id -> vector, ...}
        vector: (dim1, dim2, ...)
        dimX: float 

        return: {if -> lable, ...}
        """
        # 1. find all unique group combinations (power sert).
        ids = region.get_indexes()
        houses = region.houses
        power_set = [
            subset
            for amount in range(len(ids) + 1)
            for subset in combinations(ids, amount)
        ]

        for s in power_set:
            print(s)
        # 2. calculate group loads and selfcons.
        autarky = Autarky()
        for id in power_set:
            autarky.group_self_consumption(houses.loc[houses["id"].isin(ids), ["load", "gen"]])
        # 3. combine group autarky to area autarky
    def animate(self, ax :plt.Axes):
        """Show an animatoin of the algo"""
        