import matplotlib.pyplot as plt
from src.grouping.i_grouping_algo import I_Grouping_Algo
from itertools import combinations
from collections.abc import Callable 


class Brute_Force(I_Grouping_Algo):

    def group(self, vector_dict: dict, opti_func: Callable[]) -> None:
        """
        vector_dict: {id -> vector, ...}
        vector: (dim1, dim2, ...)
        dimX: float 

        return: {if -> lable, ...}
        """
        # 1. find all unique group combinations (power sert).
        vectors = vector_dict.keys()
        power_set = [
            subset
            for r in range(len(vectors) + 1)
            for subset in combinations(vectors, r)
        ]

        for s in power_set:
            print(s)
        # 2. calculate group loads and selfcons.
        {frozenset()}
        # 3. combine group autarky to area autarky
    def animate(self, ax :plt.Axes):
        """Show an animatoin of the algo"""
        