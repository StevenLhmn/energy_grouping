from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import plotly.graph_objects as go
from src.data.region import Region
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo
from src.animation.trajectory import Trajectory

class K_Means(GroupingAlgo):

    def __init__(self, distance_weight: float, n_cluster: int, iters: int):
        self.n_cluster = n_cluster #TODO check cluster
        self.distance_weight = GroupedRegion._check_weight(distance_weight)
        self.iters = self._check_iters(iters)
        self.trajectory = Trajectory()

    def group(self, region: Region, animate: bool = True) -> GroupedRegion:
        houses = region.houses.copy()[["id", "coordinate"]]
        houses = houses.to_crs('EPSG:4326')
        houses['x'] = [coord.x  for coord in houses['coordinate']]
        houses['y'] = [coord.y  for coord in houses['coordinate']]
        houses['diffs'] = region.get_diffs()
        data = np.column_stack((houses[["x", "y"]].to_numpy(), np.asarray(houses["diffs"].tolist())))
        data_scaled = StandardScaler().fit_transform(data)

        if animate and self.iters > 1:
            for i in range(self.iters - 1):
                self._cluster(data_scaled, i, region)

        grouped_region = self._cluster(data_scaled, self.iters, region)

        return grouped_region

    def _cluster(self, data, i, region):
        kmeans = KMeans(
            n_clusters=self.n_cluster,
            max_iter=i,
            random_state=region.get_seed())
        labels = kmeans.fit_predict(data)
        labels_by_id = dict(zip(region.get_indexes(), labels))
        grouped_region = GroupedRegion(region=region, labels=labels_by_id)
        self._update_trajectory(grouped_region, i)

        return grouped_region

    def get_trajectory(self):
        return self.trajectory

    def _update_trajectory(self, grouped_region: GroupedRegion, i):
        ids = grouped_region.houses["id"]
        x = np.array([coord.x  for coord in grouped_region.houses["coordinate"]])
        y = np.array([coord.y  for coord in grouped_region.houses["coordinate"]])
        labels = list(grouped_region.get_labels().values())
        centroids = grouped_region.get_group_centroids()
        diffs = np.array([
            gen[0] - load[0] 
            for gen, load 
            in zip(grouped_region.houses["gen"], grouped_region.houses["load"])
        ])

        frame = go.Frame(
            name=str(f'iteration {i}'),
            data=[
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    marker=dict(
                        size=abs(diffs/diffs.max())*20,
                        color=labels,
                    ),
                    text=ids,
                ),

                go.Scatter(
                    x=centroids["x"],
                    y=centroids["y"],
                    mode="markers",
                    marker=dict(
                        size=20,
                        symbol="x",
                    ),
                    text=centroids["label"],
                    name="Centroids",
                ),
            ],
        )

        self.trajectory.log(frame)

    def _check_iters(self, iters):
        if iters is None:
            raise ValueError(f'iters must be specified. But was {iters}')
        if not isinstance(iters, int):
            raise TypeError(f'iters must be an integer. But was {type(iters)}')
        if iters <= 0:
            raise ValueError(f'iters must be greater than 0. But was {iters}')
        
        return iters

    def __str__(self):
        return "K Means"