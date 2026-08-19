from time import perf_counter
from src.data.region import Region
from src.grouping.grouping_algo import GroupingAlgo

class Measurement:
    def __init__(self, region: Region, algo: GroupingAlgo):
        self.region = region
        self.algo = algo
        self._measure()

    def _measure(self):
        self.start = perf_counter()
        self.algo.group(self.region)
        self.end = perf_counter()

    def __str__(self):
        return f'{self.algo}: {self.region.house_amount()} Houses in {self.get_duration()} seconds'

    def get_duration(self) -> float:
        """
        retunrs float value as seconds
        """
        return self.end - self.start
