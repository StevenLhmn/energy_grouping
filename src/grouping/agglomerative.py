import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
from itertools import combinations
from src.data.region import Region
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo
from src.animation.trajectory import Trajectory

class Agglomerative(GroupingAlgo):

    _trajectory: Trajectory = None

    def __init__(self, distance_weight: float, max_clusters: int = None):
        self.distance_weight = GroupedRegion._check_weight(distance_weight)
        if max_clusters is not None:
            if not isinstance(max_clusters, int):
                raise TypeError("max_clusters must be an integer or None")
            if max_clusters <= 0:
                raise ValueError("max_clusters must be greater than 0")
        self.max_clusters = max_clusters
        self._trajectory = Trajectory()

    def __str__(self):
        return "Agglomerative"

    def group(self, region:Region, Animate=True):
        indexes = region.get_indexes().tolist()
        gen_load = region.houses.loc[:, ["id", "gen", "load"]].copy()

        cluster_dissimilarities = pd.DataFrame(
            np.nan, index=indexes, columns=indexes
        )

        for index in indexes:
            cluster_dissimilarities.at[index, index] = 0.0

        for left, right in combinations(indexes, 2):
            distance = region.get_dissimilarity(left, right)  # Your distance calculation
            cluster_dissimilarities.at[left, right] = distance
            cluster_dissimilarities.at[right, left] = distance

        while group_size > self.max_clusters:
            self._smalles(tcluster_dissimilarities)

        self.result = GroupedRegion(region, labels=[])

    def get_trajectory(self, trajectory: Trajectory):
        pass

    def _smallest(self, matrix: pd.Dataframe):
        upper = matrix.where(
            np.triu(np.ones(matrix.shape, dtype=bool), k=1)
        )

        left, right = upper.stack().idxmin()
        smallest = upper.loc[left, right]