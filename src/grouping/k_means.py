from src.data.region import Region
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo
class K_Means(GroupingAlgo):

    def __init__(self, distance_weight: float):
        self.distance_weight = GroupedRegion._check_weight(distance_weight)

    def group(self, region: Region):
        houses = region.houses.copy()[["id", "coordinate"]]
        houses = houses.to_crs('EPSG:4326')
        houses['x'] = [coord.x  for coord in houses['coordinate']]
        houses['y'] = [coord.y  for coord in houses['coordinate']]
        houses["diffs"] = region.get_diffs()
        data = houses[["x", "y", "diffs"]]

        data_scaled = StandardScaler().fit_transform(X)

        kmeans = KMeans(n_clusters=3, random_state=42)
        df["cluster"] = kmeans.fit_predict(X_scaled)

        vector_list = houses[diff, x, y]

    def animate(self):
        pass

    def __str__(self):
        return "K Means"