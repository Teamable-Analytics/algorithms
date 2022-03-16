from algorithm.consts import DEFAULT
from student import Student


class SocialGraphException(Exception):
    pass


class SocialGraph:
    _social_graph = {}
    degree = float('-inf')

    def __init__(self, students: [Student]):
        self._social_graph = self._create_social_graph(students)
        self.degree = float('-inf')

    def _create_social_graph(self, students: [Student]):
        social_graph = {}
        max_degree = 0
        for student in students:
            student_node_degree = 0
            for other in students:
                if student.id == other.id:  # self-edges are not allowed
                    continue
                social_graph[(student.id, other.id)] = student.relationships[other.id] if other.id in student.relationships else DEFAULT
                student_node_degree += 1
            max_degree = max(max_degree, student_node_degree)
        return social_graph

    def add_or_update_edge(self, from_id: int, to_id: int, value: float):
        self._social_graph[(from_id, to_id)] = value

    def edge_exists(self, from_id: int, to_id: int) -> bool:
        if (from_id, to_id) not in self._social_graph.keys():
            return False
        return self._social_graph[(from_id, to_id)]

    def get_edge(self, from_id: int, to_id: int) -> float:
        if (from_id, to_id) not in self._social_graph.keys():
            raise SocialGraphException(f'No edge exists {from_id} -> {to_id}')
        return self._social_graph[(from_id, to_id)]
