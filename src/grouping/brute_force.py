import numpy as np
import plotly.graph_objects as go
from plotly.colors import qualitative
from itertools import combinations
from src.data.region import Region
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo
from src.animation.trajectory import Trajectory


class Brute_Force(GroupingAlgo):

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

    def group(self, region: Region, animate=True):
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
            if self.max_clusters is not None and len(partition) > self.max_clusters:
                continue
            partition_autarky = 0
            labels = {}
            for label, group in enumerate(partition):
                for id in group:
                    labels[id] = label
            grouped_region = GroupedRegion(region, labels=labels)
            partition_score = grouped_region.region_score(self.distance_weight)
            if best_partition is None or partition_score > best_partition[0]:
                best_partition = (partition_score, labels)
                if animate:
                    yield self._update_trajectory(grouped_region)
        
        self._result = GroupedRegion(region, labels=best_partition[1])

    def result(self):
        return self._result

    def get_trajectory(self):
        return self.trajectory

    def _update_trajectory(self, grouped_region: GroupedRegion) -> go.Frame:
        """Create the final frame for an exhaustive search."""
        houses = grouped_region.houses
        ids = houses["id"].to_numpy()
        x = np.array([coordinate.x for coordinate in houses["coordinate"]])
        y = np.array([coordinate.y for coordinate in houses["coordinate"]])
        labels = np.asarray(list(grouped_region.get_labels().values()))
        colors = {
            label: qualitative.Plotly[int(label) % len(qualitative.Plotly)]
            for label in sorted(set(labels))
        }
        frame = go.Frame(
            name=f"partition",
            data=[],
            layout=go.Layout(
                meta={"score": float(grouped_region.region_score(self.distance_weight))},
                title_text=(
                    f"final result | score "
                    f"{grouped_region.region_score(self.distance_weight):.3f} | "
                    f"groups {len(set(labels))}"
                ),
            ),
        )
        for label, color in colors.items():
            mask = labels == label
            frame.data += (go.Scatter(
                x=x[mask],
                y=y[mask],
                mode="markers",
                marker=dict(size=10, color=color),
                text=ids[mask],
                name=f"Label {label}",
                legendgroup=f"label-{label}",
            ),)
        self._trajectory.log(frame)
        return frame

