from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class I_Grouping_Algo(ABC):

    @abstractmethod
    def group(self, vector_list: list) -> None:
        """vector: point, dimensions: x, y, z, 
        [
            point[
                x,
                y,
                ...],
            point[
                x,
                y,
                ...],
            point[
                ...
            ],
            ...,
        ]
        """

    @abstractmethod
    def animate(self, ax :plt.Axes):
        """Show an animatoin of the algo"""
        