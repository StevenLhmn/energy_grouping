from shapely.geometry import Point
import numpy as np
import geopandas as gpd

class Region:
    houses: gpd.GeoDataFrame = None 
    def __init__(self, houses):
        '''
            houses is a gdf with columns ['gen', 'load', 'coordinate']
            in gen and load are np.ndarrays with the same lenghth
            in coordinate are points(x, y) in epsg: 4326
            the coordinate cant be the same for 2 houses
        '''
        self.houses = self._check_houses(houses)


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

        return houses

    def _index_houses(self):
        # use a hash including the cordiante and a unique id to index each house 
        
        ids = []
        for _, row in self.houses.iterrows():
            id = f'{row.x} + {row.y}'
            print(id)
            if id in ids:
                raise ValueError(f'Duplicate coordinate found at: {id}')
            ids += [id]
        self.houses["id"] = ids


    def get_indexes(self):
        """
            No house can have the same index and the house will keeep the index for the rest of the time.
        """        
        return self.houses["id"]
        