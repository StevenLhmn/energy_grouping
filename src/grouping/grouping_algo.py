from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


class GroupingAlgo(ABC):
    @abstractmethod
    def group(self) -> None:
        """Group the regions."""
        pass

    @abstractmethod
    def animate(self, ax: plt.Axes) -> None:
        """Show an animation of the algorithm."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return a readable algorithm name."""
        pass