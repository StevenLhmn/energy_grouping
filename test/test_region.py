import unittest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from src.data.region import Region


class Test_Region(unittest.TestCase):

    def test_valid_houses_is_accepted(self):
        houses_gdf = gpd.GeoDataFrame(
            {
                "gen": [np.array([1, 2, 3])],
                "load": [np.array([1, 2, 3])],
                "coordinate": [Point(0, 0)],
            },
            geometry="coordinate",
            crs="EPSG:4326",
        )

        region = Region(houses=houses_gdf)

        self.assertIsInstance(region, Region)
        self.assertTrue(region.houses.equals(houses_gdf))
        
    def test_wrong_gen_length(self):
        # Create a GeoDataFrame with inconsistent gen and load lengths
        wrong_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [
                    np.array([1, 2, 3]),
                    np.array([4, 5]),
                    np.array([7, 8, 9])],
                'load': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2)]
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for inconsistent lengths
        with self.assertRaises(ValueError):
            Region(houses=wrong_houses_gdf)

    def test_wrong_load_length(self):
        # Create a GeoDataFrame with inconsistent gen and load lengths
        wrong_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'load': [
                    np.array([1, 2]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2)]
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for inconsistent lengths
        with self.assertRaises(ValueError):
            Region(houses=wrong_houses_gdf)

    def test_wrong_coordinate_type(self):
        # Create a GeoDataFrame with a wrong coordinate type
        wrong_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'load': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Polygon([(0, 0), (1, 1), (0, 1)]),  # Wrong type: Polygon instead of Point
                    Point(1, 1),
                    Point(2, 2)]
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for wrong coordinate type
        with self.assertRaises(TypeError):
            Region(houses=wrong_houses_gdf)

    def test_missing_columns(self):
        # Create a GeoDataFrame missing the 'load' column
        wrong_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2)]
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for missing columns
        with self.assertRaises(ValueError):
            Region(houses=wrong_houses_gdf)

    def test_extra_columns(self):
        # Create a GeoDataFrame with extra columns
        wrong_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'load': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2)],
                'extra_column': [1, 2, 3]  # Extra column
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for extra columns
        with self.assertRaises(ValueError):
            Region(houses=wrong_houses_gdf)

    def test_empty_dataframe(self):
        # Create an empty GeoDataFrame
        empty_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [],
                'load': [],
                'coordinate': []
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for empty DataFrame
        with self.assertRaises(ValueError):
            Region(houses=empty_houses_gdf)
    
    def test_non_geodataframe_input(self):
        # Create a non-GeoDataFrame input (e.g., a regular DataFrame)
        non_gdf_input = pd.DataFrame(
            {
                'gen': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'load': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2)]
            }
        )

        # Verify that the Region constructor raises an error for non-GeoDataFrame input
        with self.assertRaises(TypeError):
            Region(houses=non_gdf_input)

    def test_gen_not_np_array(self):
        # Create a GeoDataFrame with 'gen' not being a numpy array
        wrong_houses_gdf = gpd.GeoDataFrame(
            {
                'gen': [
                    [1, 2, 3],  # List instead of np.array
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'load': [
                    np.array([1, 2, 3]),
                    np.array([4, 5, 6]),
                    np.array([7, 8, 9])],
                'coordinate': [
                    Point(0, 0),
                    Point(1, 1),
                    Point(2, 2)]
            },
            geometry='coordinate',
            crs="EPSG:4326"
        )

        # Verify that the Region constructor raises an error for 'gen' not being a numpy array
        with self.assertRaises(TypeError):
            Region(houses=wrong_houses_gdf)


if __name__ == '__main__':
    unittest.main()
