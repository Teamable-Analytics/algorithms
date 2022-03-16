from itertools import combinations

from algorithm.consts import DEFAULT
from student import Student

"""
Raw -> (from_id, to_id): relationship    (directed)
Levelled -> (from_id, to_id): if_exists  (undirected, depends on current graph level)
Subgraph -> member_id: [other_ids...]    (undirected, depends on current graph level)

All separate graph representations
"""


class SocialGraphException(Exception):
    pass


class SocialGraph:
    _social_graph = {}

    def __init__(self, students: [Student], level: float):
        self.level = level
        self.students = students
        self._raw_social_graph = self._create_social_graph(students)
        self._social_graph = self.level_graph(level)

    def level_graph(self, level: float) -> dict:
        levelled_social_graph = {}
        for student, other in combinations(self.students, 2):
            total_relationship = self._raw_social_graph[(student.id, other.id)] + \
                                 self._raw_social_graph[(other.id, student.id)]
            if total_relationship <= level:  # being at this level or better means having a lighter or the same weight
                levelled_social_graph[(student.id, other.id)] = levelled_social_graph[(other.id, student.id)] = True
        return levelled_social_graph

    def _create_social_graph(self, students: [Student]):
        social_graph = {}
        for student in students:
            for other in students:
                if student.id == other.id:  # self-edges are not allowed
                    continue
                social_graph[(student.id, other.id)] = DEFAULT
                if other.id in student.relationships:
                    # update to real relationship value if one exists
                    social_graph[(student.id, other.id)] = student.relationships[other.id]
        return social_graph

    def subgraph(self, member_ids: [int]):
        subgraph = {member_id: [] for member_id in member_ids}
        for (from_id, to_id), edge_exists in self._social_graph.items():
            if from_id not in member_ids or to_id not in member_ids:
                continue
            if edge_exists:
                subgraph[from_id].append(to_id)
        return subgraph
