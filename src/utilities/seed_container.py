import secrets
import numpy as np

class Seed_Container:
    def __init__(self, seed: int = None):
        if seed is None:
            seed = secrets.randbelow(2**32)
        elif seed <= 0:
            raise ValueError(f'seed is {seed} but may not be below 0')
        elif seed > 2**32:
            raise ValueError(f'seed is {seed} but may not be above 2**32')
        self.seed = seed

    def seed(self):
        return self.seed

    def rng(self) -> np.random.Generator:
        return np.random.default_rng(self.seed)