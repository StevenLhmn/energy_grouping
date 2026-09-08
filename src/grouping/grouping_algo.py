from abc import ABC, abstractmethod
from src.data.grouped_region import GroupedRegion


class GroupingAlgo(ABC):
    @abstractmethod
    def group(self) -> GroupedRegion:
        """Group the regions."""
        pass

    @abstractmethod
    def get_trajectory(self) -> None:
        """Get the animation data in form of trajectory object."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return a readable algorithm name."""
        pass