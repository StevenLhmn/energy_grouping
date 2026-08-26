import geopandas as gpd
import numpy as np
from shapely.geometry import Point



class Region:
    houses: gpd.GeoDataFrame = None 
    def __init__(self, houses):
        '''
            houses is a gdf with columns ['gen', 'load', 'coordinate']
            in gen and load are np.ndarrays with the same lenghth
            in coordinate are points(x, y) in epsg: 4326
            the coordinate cant be the same for 2 houses
        '''
        self.houses = self._check_houses(houses).copy()
        self._index_houses()


    def _check_houses(self, houses):
        if not isinstance(houses, gpd.GeoDataFrame):
            raise TypeError("houses must be a GeoDataFrame")

        # Check if all required columns are present in the GeoDataFrame and not any others
        required_columns = ['gen', 'load', 'coordinate']
        if not all(col in houses.columns for col in required_columns):
            raise ValueError(f'houses must contain the columns: {required_columns}')
        if len(houses.columns) != len(required_columns):
            raise ValueError(f'houses must only contain the columns: {required_columns}')

        # check lead and gen are numpy arrays   
        for col in ['gen', 'load']:
            if not all(isinstance(arr, np.ndarray) for arr in houses[col]):
                raise TypeError(f'Column {col} must contain numpy arrays')

        # Check that all arrays in 'gen' and 'load' have the same length
        gen_lengths = [len(arr) for arr in houses['gen']]
        load_lengths = [len(arr) for arr in houses['load']]
        if not (len(set(gen_lengths)) == 1 and len(set(load_lengths)) == 1):
            raise ValueError("All arrays in 'gen' and 'load' columns must have the same length")

        # Check that the lengths of 'gen' and 'load' are equal
        if gen_lengths[0] != load_lengths[0]:
            raise ValueError(f'Arrays in gen and load columns must have the same length. But was gen: {gen_lengths[0]} vs load: {load_lengths[0]}')
           
        # Check that all coordinates are Point objects
        if not all(isinstance(coord, Point) for coord in houses['coordinate']):
            raise TypeError("Column 'coordinate' must contain Point objects")

        # Check that gdf gemometry is set to the coordinate column
        try:
            if houses.geometry.name != 'coordinate':
                pass
        except AttributeError:
            raise ValueError("GeoDataFrame must have a geometry column named 'coordinate'")

        # Check that the GeoDataFrame has a valid CRS
        if not houses.crs in ['EPSG:4326', 'EPSG:3857']:
            raise ValueError("GeoDataFrame must be EPSG:4326")

        return houses

    def _index_houses(self):
        ids = []
        seen = set()

        for coord in self.houses["coordinate"]:
            key = (round(coord.x, 6), round(coord.y, 6))

            if key in seen:
                raise ValueError(f"Duplicate coordinate found at: {key}")

            seen.add(key)

            id = f"X{key[0]:.6f}|Y{key[1]:.6f}"
            ids.append(id)

        self.houses["id"] = ids


    def get_indexes(self) -> list[str]:
        """
            No house can have the same index and the house will keeep the index for the rest of the time.
        """        
        return self.houses["id"]

    def house_amount(self):        
        return self.houses.shape[0]

    def get_diffs(self):
        diffs = self.houses["gen"] - self.houses["load"]
        return diffs.to_list()