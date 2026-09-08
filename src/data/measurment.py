from time import perf_counter
from src.data.region import Region
from src.grouping.grouping_algo import GroupingAlgo

class Measurement:
    def __init__(self, region: Region, algo: GroupingAlgo):
        self.algo = algo
        self.run(region)

    def run(self, region: Region) -> float:
        """Run the algorithm for a region and return the duration in seconds."""
        self.region = region
        self.start = perf_counter()
        self.grouped_region = self.algo.group(self.region)
        self.end = perf_counter()
        return self.get_duration()

    def __str__(self):
        duration = self.get_duration()
        return f'{duration:.6f}'

    def __repr__(self):
        n_houses = self.region.house_amount()
        duration = self.get_duration()
        return f'{self.algo}: {n_houses} Houses in {duration:.3f} seconds'

    def get_duration(self) -> float:
        """
        retunrs float value as seconds
        """
        return self.end - self.start
