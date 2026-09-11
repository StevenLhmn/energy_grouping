import numpy as np
import plotly.graph_objects as go
from plotly.colors import qualitative
from collections.abc import Iterator
from src.data.grouped_region import GroupedRegion
from src.grouping.grouping_algo import GroupingAlgo
from src.data.region import Region
from src.animation.trajectory import Trajectory
from src.utilities.seed_container import Seed_Container

class Genetic(GroupingAlgo):
    _trajectory: Trajectory = None
    distance_weight: float = None
    sc: Seed_Container = None

    def __init__(self, seed_container: Seed_Container, distance_weight: float, n_groups : int, iters: int = 10):
        """
        distance weight: float, 0-1
        iters: int, 0-intmax
        """
        self.distance_weight = GroupedRegion._check_weight(distance_weight)
        self.iters = self._check_iters(iters)
        self._trajectory = Trajectory()
        self.sc = seed_container
        self.n_groups = n_groups
        self.result = None

    def __str__(self) -> str:
            """Return a readable algorithm name."""
            return "Genetic"

    def group(self, region: Region, animate: bool = True) -> Iterator[go.Frame]:
        """Yield optimization frames and save the final result internally."""
        if not isinstance(region, Region):
            raise TypeError(f"region must be a Region. But was {type(region)}")

        self._trajectory = Trajectory()
        self.result = None
        population = self._init_population(region)
        fitness = self._determine_fitness(population, region)
        if animate:
            yield self._update_trajectory(region, population, fitness, 0)

        for i in range(1, self.iters):
            left_over = self._select(population, fitness)
            population = self._crossover(left_over, region.house_amount())
            population = self._mutate(population)
            fitness = self._determine_fitness(population, region)
            if animate:
                yield self._update_trajectory(region, population, fitness, i)

        best = population[int(np.argmax(fitness))]
        self.result = GroupedRegion(
            region,
            self._labels_from_chromosome(best, region)
        )

    def get_result(self) -> GroupedRegion:
        """Return the result produced by the most recently consumed run."""
        return self.result
    def get_trajectory(self) -> Trajectory:
        """Get the animation data in form of trajectory object."""
        return self._trajectory

    def _init_population(self, region: Region):
        """Create random label chromosomes for the active region."""

        house_count = region.house_amount()
        population_size = max(4, min(20, house_count * 2))
        return [
            self.sc.rng().integers(0, self.n_groups, size=house_count, dtype=int)
            for _ in range(population_size)
        ]

    def _determine_fitness(self, population, region):
        """Return the score of every chromosome in ``population``."""
        return np.asarray([
            GroupedRegion(region, self._labels_from_chromosome(chromosome, region))
            .region_score(self.distance_weight)
            for chromosome in population
        ])

    def _select(self, population, fitness):
        """Keep the fittest half of the population, including the best item."""
        if len(population) != len(fitness) or len(population) == 0:
            raise ValueError("population and fitness must have the same non-zero length")
        count = max(2, (len(population) + 1) // 2)
        indexes = np.argsort(fitness)[-count:][::-1]
        return [np.array(population[index], dtype=int, copy=True) for index in indexes]

    def _crossover(self, parents, house_amount: int):
        """Create a full population using single-point crossover."""
        if len(parents) < 2:
            raise ValueError("at least two parents are required")
        population = [np.array(parent, dtype=int, copy=True) for parent in parents]
        target_size = max(4, min(20, house_amount * 2))
        while len(population) < target_size:
            first, second = self.sc.rng().choice(len(parents), size=2, replace=False)
            crossover_point = self.sc.rng().integers(1, len(parents[first]))
            child = np.concatenate((parents[first][:crossover_point], parents[second][crossover_point:]))
            population.append(child)
        return population

    def _mutate(self, population):
        """Mutate one random gene in each non-elite chromosome."""
        house_count = len(population[0])
        mutated = [np.array(chromosome, dtype=int, copy=True) for chromosome in population]
        for chromosome in mutated[1:]:
            if self.sc.rng().random() < 0.7:
                index = self.sc.rng().integers(0, house_count)
                chromosome[index] = self.sc.rng().integers(0, self.n_groups)
        return mutated

    def _labels_from_chromosome(self, chromosome, region: Region):
        """Convert a chromosome into the label mapping used by GroupedRegion."""
        chromosome = np.asarray(chromosome)
        if chromosome.shape != (region.house_amount(),):
            raise ValueError("chromosome length must match the number of houses")
        return dict(zip(region.get_indexes(), chromosome.astype(int).tolist()))

    def _check_iters(self, iters):
        """Validate the positive number of genetic iterations."""
        if iters is None:
            raise ValueError(f"iters must be specified. But was {iters}")
        if not isinstance(iters, int):
            raise TypeError(f"iters must be an integer. But was {type(iters)}")
        if iters <= 0:
            raise ValueError(f"iters must be greater than 0. But was {iters}")
        return iters

    def _update_trajectory(self, region, population, fitness, i):
        best = population[int(np.argmax(fitness))]
        grouped_region = GroupedRegion(
            region,
            self._labels_from_chromosome(best, region)
        )
        houses = region.houses
        ids = houses["id"]
        x = np.array([coord.x for coord in houses["coordinate"]])
        y = np.array([coord.y for coord in houses["coordinate"]])
        labels = list(grouped_region.get_labels().values())
        colors = {
            label: qualitative.Plotly[int(label) % len(qualitative.Plotly)]
            for label in sorted(set(labels))
        }
        diffs = np.array([
            gen[0] - load[0]
            for gen, load in zip(houses["gen"], houses["load"])
        ])
        sizes = np.nan_to_num(np.abs(diffs), nan=0.0, posinf=0.0, neginf=0.0)
        max_size = np.max(sizes, initial=0)
        if max_size == 0:
            sizes = np.full(len(sizes), 10.0)
        else:
            sizes = np.maximum(sizes / max_size * 20, 7)
        frame = go.Frame(
            name=str(f'iteration {i}'),
            data=[],
            layout=go.Layout(
                meta={"score": float(fitness.max())},
                title_text=(
                    f"iteration {i} | score {fitness.max():.3f} | "
                    f"groups {len(set(labels))}"
                )
            ),
        )

        point_colors = [colors[label] for label in labels]
        frame.data += (go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(size=sizes, color=point_colors),
            text=ids.tolist(),
            customdata=np.asarray(labels),
            name="Houses",
            hovertemplate="House %{text}<br>Group %{customdata}<extra></extra>",
        ),)

        self._trajectory.log(frame)
        return frame