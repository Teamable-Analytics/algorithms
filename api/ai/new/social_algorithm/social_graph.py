from itertools import combinations
from typing import Tuple, List, Dict

from api.models.enums import Relationship
from api.models.student import Student


class SocialGraph:
    def __init__(self, students: List[Student], level: float):
        self.level = level
        self.students = students
        self._raw_social_graph = create_social_graph(students)
        self._social_graph = self.level_graph(level)

    def level_graph(self, level: float) -> Dict[Tuple[int, int], bool]:
        """
        Levelled Graph (undirected) -> (from_id, to_id): if_exists : Dict[Tuple[int, int], True]
        Only edges left are those with weights equal to or lighter than self.level
        """
        levelled_social_graph = {}
        for student, other in combinations(self.students, 2):
            total_relationship = (
                self._raw_social_graph[(student.id, other.id)]
                + self._raw_social_graph[(other.id, student.id)]
            )
            if (
                total_relationship <= level
            ):  # being at this level or better means having a lighter or the same weight
                levelled_social_graph[(student.id, other.id)] = levelled_social_graph[
                    (other.id, student.id)
                ] = True
        return levelled_social_graph

    def has_edge(self, from_id: int, to_id: int) -> bool:
        if (from_id, to_id) not in self._social_graph:
            return False
        return self._social_graph[(from_id, to_id)]

    def edges(self) -> List[Tuple[int, int]]:
        return [
            (from_id, to_id)
            for (from_id, to_id), exists in self._social_graph.items()
            if exists
        ]


def create_social_graph(students: List[Student]):
    """
    Raw Social Graph (directed) -> {(from_id, to_id): relationship} : Dict[Tuple[int, int], float]
    """
    social_graph = {}
    for student in students:
        for other in students:
            if student.id == other.id:  # self-edges are not allowed
                continue
            social_graph[(student.id, other.id)] = Relationship.DEFAULT.value
            if other.id in student.relationships:
                # update to real relationship value if one exists
                social_graph[(student.id, other.id)] = student.relationships[
                    other.id
                ].value
    return social_graph
