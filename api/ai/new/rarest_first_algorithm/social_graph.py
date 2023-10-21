from itertools import combinations
from typing import List, Tuple, Dict

from api.models.enums import Relationship
from api.models.student import Student


class RawSocialGraph:
    social_graph: Dict[int, Dict[int, float]]
    distances: Dict[int, Dict[int, float]]

    def __init__(self, students: List[Student]):
        self.students = students
        self.student_id_trace = {student.id: student for student in students}
        self.social_graph = self._create_social_graph()
        self.distances = self._find_distances()

    def has_edge(self, from_id: int, to_id: int) -> bool:
        if (from_id, to_id) not in self.social_graph:
            return False
        return (from_id, to_id) in self.social_graph

    def edges(self) -> List[Tuple[int, int]]:
        return [
            (from_id, to_id)
            for (from_id, to_id), exists in self.social_graph.items()
            if exists
        ]

    def _create_social_graph(self) -> Dict[int, Dict[int, float]]:
        """
        Raw Social Graph (directed) -> {(from_id, to_id): relationship} : Dict[Tuple[int, int], float]
        """
        social_graph: Dict[int, Dict[int, float]] = {}
        for student, other in combinations(self.students, 2):
            if student.id == other.id:  # self-edges are not allowed
                continue

            if student.id not in social_graph:
                social_graph[student.id] = {}
            social_graph[student.id][other.id] = Relationship.DEFAULT.value
            if other.id in student.relationships:
                # update to real relationship value if one exists
                social_graph[student.id][other.id] = student.relationships[
                    other.id
                ].value
            # Dijkstra's algorithm requires all edges to be positive
            social_graph[student.id][other.id] += Relationship.FRIEND.value

            if other.id not in social_graph:
                social_graph[other.id] = {}
            social_graph[other.id][student.id] = Relationship.DEFAULT.value
            if student.id in other.relationships:
                # update to real relationship value if one exists
                social_graph[other.id][student.id] = other.relationships[
                    student.id
                ].value
            # Dijkstra's algorithm requires all edges to be positive
            social_graph[other.id][student.id] += Relationship.FRIEND.value

        return social_graph

    def _find_distances(self) -> Dict[int, Dict[int, float]]:
        distances: Dict[int, Dict[int, float]] = {}

        for student in self.students:
            distances[student.id] = self._find_distance(student)

        return distances

    def _find_distance(self, start_student: Student) -> Dict[int, float]:
        """
        Dijkstra's algorithm implementation
        """
        current = start_student
        current_distance = 0
        unvisited = {other.id: None for other in self.students}
        visited: Dict[int, float] = {}
        unvisited[current.id] = current_distance

        while True:
            for neighbour in self.students:
                if neighbour.id == current.id:
                    continue
                distance = self.social_graph[current.id][neighbour.id]
                if neighbour.id not in unvisited:
                    continue

                new_distance = current_distance + distance
                if (
                    unvisited[neighbour.id] is None
                    or unvisited[neighbour.id] > new_distance
                ):
                    unvisited[neighbour.id] = new_distance

            visited[current.id] = current_distance
            del unvisited[current.id]
            if len(unvisited) == 0:
                break

            candidates = [node for node in unvisited.items() if node[1]]

            if len(candidates) == 0:
                break
            current_id, currentDistance = sorted(candidates, key=lambda x: x[1])[0]
            current = self.student_id_trace[current_id]

        return visited

    def get_shortest_distance(
        self, start_student: Student, end_student: Student
    ) -> float:
        try:
            return self.distances[start_student.id][end_student.id]
        except KeyError:
            return float("inf")
