import unittest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from src.grouping.brute_force import Brute_Force
from src.data_gen.region_generator import RegionGenerator
from src.grouping.genetic import Genetic
from src.utilities.seed_container import Seed_Container


class Test_Genetic(unittest.TestCase):

    def setUp(self):
        sc = Seed_Container(seed=42)
        self.algo = Genetic(
            seed_container=sc,
            distance_weight=0.5,
            iters=1
        )
        gdf = gpd.GeoDataFrame(
                    {
                        "coordinate": [
                            Point(0, 0),
                            Point(1, 1),
                            Point(2, 2),
                        ],
                        "load": [
                                np.array([1]),
                                np.array([2]),
                                np.array([3]),
                            ],
                        "gen": [
                            np.array([3]),
                            np.array([2]),
                            np.array([1]),
                        ]   
                    },
                    geometry='coordinate',
                    crs="EPSG:4326"
                )
        self.region = RegionGenerator(sc).simple_from_gdf(gdf)

    def test_init_population(self):
        target = [
            np.array([0, 2, 1]),
            np.array([1, 1, 2]),
            np.array([0, 2, 0]),
            np.array([0, 1, 2]),
            np.array([2, 2, 2]),
            np.array([2, 1, 0])
        ]
        result = self.algo._init_population(self.region)
        self._assert_same_list_of_arrays(result, target)

    def test_labels_from_chromosome(self):
        chromosome = np.array([0, 1, 2])
        target = {"X0.000000|Y0.000000": 0,
                  "X1.000000|Y1.000000": 1,
                  "X2.000000|Y2.000000": 2,}
        label = self.algo._labels_from_chromosome(chromosome, self.region)
        if not np.array_equal(label, target):
            raise AssertionError(f'not equal: target {target}, label: {label}')


    def test_determine_fitness(self):
        population = [
            np.array([0, 2, 1]),
            np.array([1, 1, 2]),
            np.array([0, 2, 0]),
            np.array([0, 1, 2]),
            np.array([2, 2, 2]),
            np.array([2, 1, 0])
        ]
        target = [
            np.float64(0.8333333333333333),
            np.float64(0.5833613549063774),
            np.float64(0.500017954283559),
            np.float64(0.8333333333333333),
            np.float64(0.5),
            np.float64(0.8333333333333333)
        ]
        fitness = self.algo._determine_fitness(population, self.region)
        for i in range(len(fitness)):
            self.assertEqual(fitness[i], target[i])

    def test_select(self):
        target = [
            np.array([2, 1, 0]),
            np.array([0, 1, 2]),
            np.array([0, 2, 1])
        ]
        population = [
            np.array([0, 2, 1]),
            np.array([1, 1, 2]),
            np.array([0, 2, 0]),
            np.array([0, 1, 2]),
            np.array([2, 2, 2]),
            np.array([2, 1, 0])
        ]
        fitness = [
            np.float64(0.8333333333333333),
            np.float64(0.5833613549063774),
            np.float64(0.500017954283559),
            np.float64(0.8333333333333333),
            np.float64(0.5),
            np.float64(0.8333333333333333)
        ]
        selection = self.algo._select(population, fitness)
        self._assert_same_list_of_arrays(selection, target)

    def test_crossover(self):
        parents = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([7, 8, 9])
        ]
        target = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([7, 8, 9]),
            np.array([1, 8, 9]),
            np.array([7, 8, 3]),
            np.array([1, 2, 9])
        ]
        population = self.algo._crossover(parents, self.region.house_amount())
        self._assert_same_list_of_arrays(population, target)

    def test_mutation(self):
        target = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([7, 8, 9]),
            np.array([10, 11, 12]),
            np.array([13, 14, 15]),
            np.array([16, 2, 18]),
            np.array([19, 20, 21]),
            np.array([22, 23, 24]),
            np.array([25, 26, 1]),
        ]
        population = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([7, 8, 9]),
            np.array([10, 11, 12]),
            np.array([13, 14, 15]),
            np.array([16, 17, 18]),
            np.array([19, 20, 21]),
            np.array([22, 23, 24]),
            np.array([25, 26, 27]),
        ]
        new_pop = self.algo._mutate(population)
        self._assert_same_list_of_arrays(new_pop, target)

    def _assert_same_list_of_arrays(self, result, target):
        if not len(target) == len(result) and len(target) >= 0:
            raise AssertionError(f'len of target was: {len(target)}, result was {len(result)}')
        for i in range(len(target)):
            if not np.array_equal(target[i], result[i]):
                raise AssertionError(f'target: {target[i]} result: {result[i]}')

if __name__ == '__main__':
    unittest.main()
