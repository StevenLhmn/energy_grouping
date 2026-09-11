from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import plotly.graph_objects as go
from plotly.colors import qualitative
from src.data.region import Region
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo
from src.animation.trajectory import Trajectory
from src.utilities.seed_container import Seed_Container
from sklearn.cluster._kmeans import kmeans_plusplus
from sklearn.metrics import pairwise_distances_argmin
from collections.abc import Iterator

class K_Means(GroupingAlgo):
    sc : Seed_Container = None
    def __init__(
        self,
        seed_container: Seed_Container,
        distance_weight: float,
        n_cluster: int,
        iters: int):
        self.n_cluster = n_cluster #TODO check cluster
        self.distance_weight = GroupedRegion._check_weight(distance_weight)
        self.iters = self._check_iters(iters)
        self.trajectory = Trajectory()
        self.sc = seed_container
        self.result = None

    def group(self, region: Region, animate: bool = True) -> Iterator[go.Frame]:
        """Yield clustering frames and save the final result internally."""
        if not isinstance(region, Region):
            raise TypeError(f"region must be a Region. But was {type(region)}")

        self.trajectory = Trajectory()
        self.result = None
        houses = region.houses.copy()[["id", "coordinate"]]
        houses = houses.to_crs('EPSG:4326')
        houses['x'] = [coord.x  for coord in houses['coordinate']]
        houses['y'] = [coord.y  for coord in houses['coordinate']]
        houses['diffs'] = region.get_diffs()
        data = np.column_stack((houses[["x", "y"]].to_numpy(), np.asarray(houses["diffs"].tolist())))
        data_scaled = StandardScaler().fit_transform(data)
        feature_weights = np.concatenate((
            np.full(2, self.distance_weight),
            np.full(data_scaled.shape[1] - 2, 1 - self.distance_weight),
        ))
        data_scaled *= feature_weights
        

        if animate and self.iters > 1:
            centers, indices = kmeans_plusplus(
                data_scaled,
                n_clusters=self.n_cluster,
                random_state=self.sc.seed()
            )
            initial_labels = pairwise_distances_argmin(data_scaled, centers)
            labels_by_id = dict(zip(region.get_indexes(), initial_labels))
            grouped_region = GroupedRegion(region=region, labels=labels_by_id)
            yield self._update_trajectory(grouped_region, 0)

        for i in range(1, self.iters):
            grouped_region = self._cluster(data_scaled, i, region)
            if animate:
                yield self._update_trajectory(grouped_region, i)

        if self.iters == 1:
            grouped_region = self._cluster(data_scaled, self.iters, region)
            if animate:
                yield self._update_trajectory(grouped_region, self.iters)

        self.result = grouped_region

    def get_result(self) -> GroupedRegion:
        """Return the result produced by the most recently consumed run."""
        return self.result

    def _cluster(self, data, i, region):
        kmeans = KMeans(
            n_clusters=self.n_cluster,
            max_iter=i,
            random_state=self.sc.seed())
        labels = kmeans.fit_predict(data)
        labels_by_id = dict(zip(region.get_indexes(), labels))
        grouped_region = GroupedRegion(region=region, labels=labels_by_id)
        return grouped_region

    def get_trajectory(self):
        return self.trajectory

    def _update_trajectory(self, grouped_region: GroupedRegion, i):
        ids = grouped_region.houses["id"]
        x = np.array([coord.x  for coord in grouped_region.houses["coordinate"]])
        y = np.array([coord.y  for coord in grouped_region.houses["coordinate"]])
        labels = list(grouped_region.get_labels().values())
        centroids = grouped_region.get_group_centroids()
        colors = {
            label: qualitative.Plotly[int(label) % len(qualitative.Plotly)]
            for label in sorted(set(labels))
        }
        diffs = np.array([
            gen[0] - load[0] 
            for gen, load 
            in zip(grouped_region.houses["gen"], grouped_region.houses["load"])
        ])

        frame = go.Frame(
            name=str(f'iteration {i}'),
            data=[],
            layout=go.Layout(
                meta={"score": float(grouped_region.region_score(self.distance_weight))}
            ),
        )

        max_diff = np.max(np.abs(diffs), initial=0)
        if max_diff == 0:
            marker_sizes = np.full(len(diffs), 10.0)
        else:
            marker_sizes = np.maximum(np.abs(diffs) / max_diff * 20, 7)
        for label, color in colors.items():
            mask = np.array(labels) == label
            frame.data += (go.Scatter(
                x=x[mask],
                y=y[mask],
                mode="markers",
                marker=dict(size=marker_sizes[mask], color=color),
                text=ids[mask],
                name=f"Label {label}",
                legendgroup=f"label-{label}",
            ),)

        for _, centroid in centroids.iterrows():
            label = int(centroid["label"])
            frame.data += (go.Scatter(
                x=[centroid["x"]],
                y=[centroid["y"]],
                mode="markers",
                marker=dict(
                    size=16,
                    symbol="x",
                    color=colors[label],
                    line=dict(color=colors[label], width=0.8),
                ),
                text=[f"Centroid {label}"],
                name=f"Centroid {label}",
                legendgroup=f"label-{label}",
                showlegend=False,
            ),)

        self.trajectory.log(frame)
        return frame

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