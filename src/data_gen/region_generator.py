import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd
import secrets
from shapely import Point
from src.data.region import Region
from src.data_gen.lpg_wrapper import LPG_Wrapper

from datetime import date

class RegionGenerator:
    seed: int = None

    def __init__(self, seed: int = None):
        if seed is None:
            seed = secrets.randbelow(2**32)
        elif seed <= 0:
            raise ValueError(f'seed is {seed} but may not be below 0')
        elif seed > 2**32:
            raise ValueError(f'seed is {seed} but may not be above 2**32')
        self.seed = seed
        np.random.seed(self.seed)

    def simple(self):
        return self.simple_from_gdf(
            gpd.GeoDataFrame(
                {
                    "coordinate": [Point(0, 0),
                                   Point(1, 1),
                                   Point(2, 2),
                                   Point(3, 3)],
                    "load":  [
                        np.array([1,1,1]),
                        np.array([2,3,1]),
                        np.array([1,2,3]),
                        np.array([0,0,0])],
                    "gen":
                        [np.array([3,1,2]),
                        np.array([2,2,1]),
                        np.array([1,3,3]),
                        np.array([2,3,1])]   
                },
                geometry='coordinate',
                crs="EPSG:4326"
            )
        )

    def simple_from_gdf(self, gdf: gpd.GeoDataFrame):
        """
        Generate a Region from a GeoDataFrame of coordinates and load/gen data.

        Parameters:
        - gdf: GeoDataFrame with columns "coordinate", "load", and "gen"
        """
        return Region(gdf)

    def random(self, n_houses: int = 10, time_steps: int = 24, max_energy: int = 10):
        return Region(
            gpd.GeoDataFrame(
                {
                    "coordinate": [Point(np.random.uniform(0, 10), np.random.uniform(0, 10)) for _ in range(n_houses)],
                    "load": [np.random.randint(1, max_energy, time_steps) for _ in range(n_houses)],
                    "gen": [np.random.randint(1, max_energy, time_steps) for _ in range(n_houses)]
                },
                geometry='coordinate',
                crs="EPSG:4326"
            )
        )

    def geo_random(self, bbox: tuple, time_steps: int, max_energy: int):
        """
        Generate a Region households within a bounding box and random load/gen data.
        Doesnt guarantie a residential building, but it gets mostly residential buildings.
        It also doesnt say how many households exist in the house

        Parameters:
        - bbox: (minx, miny, maxx, maxy)
        - time_steps: length of load/gen time-series
        - max_energy: upper bound for randint generation
        """
        import osmnx as ox
        osm_tags = {"building": True, "landuse": "residential"} # 
        gdf = ox.features_from_bbox(bbox, tags=osm_tags)
        # eliminate buildings that are not within the bounding box, because the function fetches some buildings that are on the edge of the bbox
        gdf = gdf.to_crs(epsg=3857)   # so the centroid calculation is not in a degree coordinate system
        gdf['centroids_4326'] = (gpd.GeoSeries(gdf.geometry.centroid, crs=gdf.crs).to_crs(epsg=4326))
        gdf = gdf[gdf.centroids_4326.within(ox.utils_geo.bbox_to_poly(bbox))]
        centroids = gpd.GeoSeries(gdf.geometry.centroid, crs=gdf.crs).to_crs(epsg=4326)
        
        return Region(
            gpd.GeoDataFrame(
                {
                    "coordinate": centroids,
                    "load": [np.random.randint(1, max_energy, time_steps) for _ in range(len(gdf))],
                    "gen": [np.random.randint(1, max_energy, time_steps) for _ in range(len(gdf))]
                },
                geometry='coordinate',
                crs="EPSG:4326"
            )
        )

    def _eliminate_buildings_outside_bbox(self, gdf: gpd.GeoDataFrame, bbox: tuple):
        """
        Eliminate buildings that are not within the bounding box, because the function fetches some buildings that are on the edge of the bbox

        Parameters:
        - gdf: GeoDataFrame with building geometries
        - bbox: (minx, miny, maxx, maxy)
        """
        return gdf[gdf.centroid.within(ox.utils_geo.bbox_to_poly(bbox))]
    
    def _estimate_number_of_household(self, areas: pd.Series):
        """
        Estimate the number of hhs based on the area of the building footprint.
        This is a very rough estimate and should be improved in the future.

        Parameters:
        - areas: GeoSeries with building areas, in meteres
        """
        
        # rough estimate: Aparment(Footprint)=0.022Footprint^1.12
        #return np.round(0.010 * areas**1.12).astype(int)
        return np.round(0.001 * areas**1.12).astype(int) #ToDo for testing
    
    def _generate_gen_profile(self, area: gpd.GeoSeries, time_steps: int, max_energy: int):
        """
        Generates mok-pv profiles that corrospond to the area of the building footprint.

        Parameters:
        - area: GeoSeries with building areas
        - time_steps: number of time steps in the gen profile
        - max_energy: maximum energy consumption per household
        """

        slope = .5
        plateau = 3
        steps = np.array(range(time_steps))+1
        bell = np.exp(-slope * ((steps - (steps.shape[0]+1)/2) / plateau)**2) * max_energy * area
        #random noise
        bell = bell * (np.random.rand(time_steps)*.8 + .2)

        return bell

    def geo_LPG(self, bbox: tuple, time_steps: int, max_energy: int, ):# todo start end, max energy to factor 
        """
        Generate a Region households within a bounding box and assigns load/gen data based on the LoadProfileGenerator program. The house size determins how many households exist in the house. The profiles are realisic profiles based on predefined household configurations.

        Parameters:
        - bbox: (minx, miny, maxx, maxy)
        - time_steps: length of load/gen time-series
        - max_energy: upper bound for randint generation
        """
       
        osm_tags = {"building": True} 
        gdf = ox.features_from_bbox(bbox, tags=osm_tags)
        gdf = self._eliminate_buildings_outside_bbox(gdf, bbox)
        print(f'found {len(gdf)} buildings')
        gdf["n_hhs"] = self._estimate_number_of_household(gdf.to_crs(epsg=3857).area)

        gen = [self._generate_gen_profile(area, time_steps, max_energy) for area in gdf.to_crs(epsg=3857).area]
        load = [LPG_Wrapper(self.seed).generate_appartment(n_hhs, date(2022, 4, 1), date(2022, 4, 1), "1h")
            for n_hhs in gdf["n_hhs"]
        ]
        
        return Region(
            gpd.GeoDataFrame(
                { 
                    "coordinate": gdf.centroid,  
                    "load": load,
                    "gen": gen,
                },
                geometry='coordinate',
                crs="EPSG:4326"
            )
        )          
