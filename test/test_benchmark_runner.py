import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import numpy as np

from src.controller.benchmark_runner import BenchmarkRunner


class TestBenchmarkRunner(unittest.TestCase):
    def test_run_returns_one_result_for_each_combination(self):
        generator = Mock()
        generator.random.side_effect = lambda n_houses, time_steps, max_energy: Mock()
        algorithm = Mock()
        algorithm.group.return_value = Mock()

        runner = BenchmarkRunner(algorithm, generator=generator)
        with TemporaryDirectory() as directory:
            output_file = Path(directory) / "results.csv"
            results = runner.run(100, 30, 10, 10, output_file)
            saved_results = np.loadtxt(output_file, delimiter=",")

        self.assertEqual(results.shape, (10, 3))
        self.assertTrue(np.all(results >= 0))
        self.assertEqual(saved_results.shape, results.shape)
        self.assertTrue(np.allclose(saved_results, results))
        self.assertEqual(generator.random.call_count, 30)

    def test_run_rejects_non_positive_intervals(self):
        runner = BenchmarkRunner(Mock())

        with self.assertRaises(ValueError):
            runner.run(100, 30, 0, 10)


if __name__ == "__main__":
    unittest.main()