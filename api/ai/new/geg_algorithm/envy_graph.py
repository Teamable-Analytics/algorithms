from typing import List, Dict, Set

from api.models.student import Student


class EnvyGraph:
    def __init__(self, students: List[Student]) -> None:
        """
        Initialize an envy graph

        This run in O(N)
        """
        vertices = [student.id for student in students]
        self.graph: Dict[int, Set[int]] = {vertex: set([]) for vertex in vertices}
        self.additive_utilities: Dict[int, int] = {vertex: 0 for vertex in vertices}

    def add_edge(self, envy_project: int, other_project: int) -> None:
        """
        This run in O(1)
        """
        self.graph[envy_project].add(other_project)

    def remove_edge(self, no_loger_envy_project: int, other_project: int) -> None:
        """
        This run in O(1)
        """
        if other_project in self.graph[no_loger_envy_project]:
            self.graph[no_loger_envy_project].remove(other_project)

    def get_envy_targets(self, envy_student: int) -> Set[int]:
        """
        This run in O(1)
        """

        return self.graph[envy_student]

    def is_sink(self, student: int) -> bool:
        """
        A student is sink if there is no outgoing edge

        This run in O(1)
        """
        return len(self.graph[student]) == 0

    def is_source(self, student: int) -> bool:
        """
        A student is source if there is no incoming edge

        This run in O(N)
        """
        return all([student not in targets for targets in self.graph.values()])

    def update_envy_graph(self, project_id: int, new_utility_value: int) -> None:
        """
        Construct a new envy graph induced by N

        This run in O(N)
        """

        # Since this is additive, add new utility value to the existed value
        self.additive_utilities[project_id] += new_utility_value

        updated_utility = self.additive_utilities[project_id]
        for other_project_id in self.additive_utilities.keys():
            if project_id == other_project_id:
                continue

            # In case utility increases, no loger envy with some and some will start envy
            if updated_utility > self.additive_utilities[other_project_id]:
                self.remove_edge(project_id, other_project_id)
                self.add_edge(other_project_id, project_id)

            # In case utility decreases, will start envy with more and some will stop envying
            if updated_utility < self.additive_utilities[other_project_id]:
                self.add_edge(project_id, other_project_id)
                self.remove_edge(other_project_id, project_id)

            # In case utility is equal to other, noone will envy
            if updated_utility == self.additive_utilities[other_project_id]:
                self.remove_edge(project_id, other_project_id)
                self.remove_edge(other_project_id, project_id)

    def get_all_directed_cycles(self) -> List[List[int]]:
        visited = set([])
        cycles = []

        for start_node in self.graph:
            self._dfs(start_node, visited, [])

        return cycles

    def _dfs(self, node: int, visited: Set[int], path: List[int]) -> List[int]:
        if node in path:
            return path[path.index(node) :]

        if node not in visited:
            visited.add(node)
            path.append(node)
            for neighbor in self.get_envy_targets(node):
                self._dfs(neighbor, visited, path)
            path.pop()
            visited.remove(node)
