import unittest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from src.data.region import Region
from src.data_gen.region_generator import RegionGenerator
from src.utilities.seed_container import Seed_Container

class Test_RegionGenerator(unittest.TestCase):

    def test_seed_is_set(self):
        seed = 42
        generator = RegionGenerator(seed=seed)
        # Check if the seed is set correctly
        self.assertEqual(generator.seed, seed)

    def test_seed_is_negative(self):
        with self.assertRaises(ValueError):
            RegionGenerator(seed=-1)

    def test_seed_is_above_limit(self):
        with self.assertRaises(ValueError):
            RegionGenerator(seed=2**33)

    def test_seed_is_none(self):
        generator = RegionGenerator(seed=None)
        # Check if the seed is set with a random value
        self.assertIsInstance(generator.seed, int)
        self.assertTrue(generator.seed >=0)
        self.assertTrue(generator.seed <2**32)

    def test_simple_region_generation(self):
        generator = RegionGenerator()
        region = generator.simple()
        # Check if the returned object is an instance of Region, if that is true it has the right structure and the right columns
        self.assertIsInstance(region, Region)

    def test_simple_region_generation_from_gdf(self):
        generator = RegionGenerator()
        gdf = gpd.GeoDataFrame(
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
        region_from_gdf = generator.simple_from_gdf(gdf)
        self.assertIsInstance(region_from_gdf, Region)
        self.assertTrue(region_from_gdf.houses["gen"].equals(gdf["gen"]))
        self.assertTrue(region_from_gdf.houses["load"].equals(gdf["load"]))
        self.assertTrue(region_from_gdf.houses["coordinate"].equals(gdf["coordinate"]))
        self.assertTrue(region_from_gdf.houses.id.tolist() == ['X0.000000|Y0.000000', 'X1.000000|Y1.000000', 'X2.000000|Y2.000000', 'X3.000000|Y3.000000'])

    def test_random_region_generation(self):
        sc = Seed_Container(seed=42)
        generator = RegionGenerator(seed_container=sc)
        n_houses = 5
        time_steps = 10
        max_energy = 20
        region = generator.random(n_houses=n_houses, time_steps=time_steps, max_energy=max_energy)
        # Check if the returned object is an instance of Region, if that is true it has the right structure and the right columns
        self.assertIsInstance(region, Region)
        # Check if the number of houses is correct
        self.assertEqual(len(region.houses), n_houses)
        # Check if the length of load and gen arrays is correct
        for _, row in region.houses.iterrows():
            self.assertEqual(len(row['load']), time_steps)
            self.assertEqual(len(row['gen']), time_steps)
        # check if the energy values are within the expected range
            self.assertTrue(np.all(row['load'] >= 1) and np.all(row['load'] < max_energy))
            self.assertTrue(np.all(row['gen'] >= 1) and np.all(row['gen'] < max_energy))

    def test_geo_random_region_generation(self):
        generator = RegionGenerator(seed=42)
        bbox_hamburg = (10.150, 53.488, 10.152, 53.49) #crs: "EPSG:4326"
        time_steps = 10
        max_energy = 20
        #Error if no connection to the internet is available, because the function fetches data from OpenStreetMap
        region = generator.geo_random(bbox=bbox_hamburg, time_steps=time_steps, max_energy=max_energy)
        # Check if the returned object is an instance of Region, if that is true it has the right structure and the right columns
        self.assertIsInstance(region, Region)
        # Check if the length of load and gen arrays is correct
        for _, row in region.houses.iterrows():
            self.assertEqual(len(row['load']), time_steps)
            self.assertEqual(len(row['gen']), time_steps)
            # check if the energy values are within the expected range
            self.assertTrue(np.all(row['load'] >= 1) and np.all(row['load'] < max_energy))
            self.assertTrue(np.all(row['gen'] >= 1) and np.all(row['gen'] < max_energy))
            # Check if coordinates are Points
            self.assertIsInstance(row['coordinate'], Point)
            # test if the coordinates are within the bounding box
            self.assertTrue(bbox_hamburg[0] <= row['coordinate'].x <= bbox_hamburg[2])
            self.assertTrue(bbox_hamburg[1] <= row['coordinate'].y <= bbox_hamburg[3])

    def test_geo_random_region_generation_empty_region(self):
        generator = RegionGenerator(seed=42)
        bbox = (0.1, 0.1, 0.2, 0.2)  # crs: "EPSG:4326", empty region
        time_steps = 10
        max_energy = 20

        with self.assertRaises(ValueError):
            generator.geo_random(bbox=bbox, time_steps=time_steps, max_energy=max_energy)

    def test_geo_LPG(self):
        generator = RegionGenerator(seed=42)
        bbox_hamburg = (10.150, 53.488, 10.152, 53.49)  # crs: "EPSG:4326"
        time_steps = 24
        max_energy = 20
        region = generator.geo_LPG(bbox=bbox_hamburg, time_steps=time_steps, max_energy=max_energy)
        self.assertIsInstance(region, Region)
        for _, row in region.houses.iterrows():
            self.assertEqual(len(row['load']), time_steps)
            self.assertEqual(len(row['gen']), time_steps)
            # check if the energy values are within the expected range
            self.assertTrue(np.all(row['load'] >= 1) and np.all(row['load'] < max_energy))
            self.assertTrue(np.all(row['gen'] >= 1) and np.all(row['gen'] < max_energy))
            # Check if coordinates are Points
            self.assertIsInstance(row['coordinate'], Point)
            # test if the coordinates are within the bounding box
            self.assertTrue(bbox_hamburg[0] <= row['coordinate'].x <= bbox_hamburg[2])
            self.assertTrue(bbox_hamburg[1] <= row['coordinate'].y <= bbox_hamburg[3])

    def test_geo_LPG_empty_region(self):
        generator = RegionGenerator(seed=42)
        bbox = (0.1, 0.1, 0.2, 0.2)  # crs: "EPSG:4326", empty region
        time_steps = 10
        max_energy = 20

        with self.assertRaises(ValueError):
            generator.geo_LPG(bbox=bbox, time_steps=time_steps, max_energy=max_energy)

if __name__ == '__main__':
    unittest.main()