import numpy as np
from pathlib import Path
from datetime import datetime

from src.data.measurment import Measurement
from src.data_gen.region_generator import RegionGenerator


class BenchmarkRunner:
	def __init__(self, algo, generator: RegionGenerator | None = None, max_energy: int = 10):
		self.algo = algo
		self.generator = generator or RegionGenerator()
		self.max_energy = max_energy

	def run(
		self,
		max_houses: int,
		max_time_steps: int,
		house_interval: int,
		time_step_interval: int,
		file_location: str | Path = ".",
	) -> np.ndarray:
		"""Run every house-count/time-step combination.

		The returned array contains durations in seconds, indexed as
		``results[house_index][time_step_index]``.
		The same array is saved as a comma-separated CSV file.
		"""
		house_counts = self._values(max_houses, house_interval, "house")
		time_steps = self._values(max_time_steps, time_step_interval, "time-step")
		results = np.empty((len(house_counts), len(time_steps)), dtype=float)

		for house_index, house_count in enumerate(house_counts):
			for time_step_index, time_step_count in enumerate(time_steps):
				region = self.generator.random(
					n_houses=house_count,
					time_steps=time_step_count,
					max_energy=self.max_energy,
				)
				results[house_index, time_step_index] = Measurement(
					region, self.algo
				).get_duration()

		file_location = Path(file_location)
		file_location.mkdir(parents=True, exist_ok=True)
		output_file = file_location / self.file_name()
		np.savetxt(output_file, results, delimiter=",", fmt="%.9f")
		return results

	@staticmethod
	def file_name() -> str:
		return datetime.now().strftime("Zeitmessuing_%Y_%m_%d_%H_%M.csv")
	
	@staticmethod
	def _values(maximum: int, interval: int, name: str) -> range:
		if maximum <= 0:
			raise ValueError(f"max_{name}s must be positive")
		if interval <= 0:
			raise ValueError(f"{name}_interval must be positive")
		return range(interval, maximum + 1, interval)