from abc import ABC, abstractmethod
from src.data.grouped_region import GroupedRegion
from src.data.region import Region
from src.animation.trajectory import Trajectory


class GroupingAlgo(ABC):
    @abstractmethod
    def group(self, region: Region) -> GroupedRegion:
        """Group the regions."""
        pass

    @abstractmethod
    def get_trajectory(self) -> Trajectory:
        """Get the animation data in form of trajectory object."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return a readable algorithm name."""
        return