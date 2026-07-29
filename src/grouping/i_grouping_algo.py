from abc import ABC, abstractmethod

class I_Grouping_Algo(ABC):

    @abstractmethod
    def group(self, vector_list: ) -> None:
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
    def extract_text(self) -> str:
        """Return text extracted from the loaded file."""