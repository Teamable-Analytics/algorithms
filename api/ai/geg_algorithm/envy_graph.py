from typing import List, Dict, Set, Callable

from api.dataclasses.student import Student
from api.dataclasses.team import Team, TeamShell


class EnvyGraph:
    def __init__(
        self,
        teams: List[Team],
        students: List[Student],
        utility_function: Callable[[Student, TeamShell], float],
    ):
        """
        Initialize an envy graph
        """
        vertices = [team.project_id for team in teams]
        self.graph: Dict[int, Set[int]] = {vertex: set([]) for vertex in vertices}
        self.additive_utilities: Dict[int, int] = {vertex: 0 for vertex in vertices}
        self.project_id_traces: Dict[int, Team] = {t.project_id: t for t in teams}
        self.student_id_traces: Dict[int, Student] = {s.id: s for s in students}
        self.utility_function = utility_function

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

    def get_envy_targets(self, envy_project: int) -> Set[int]:
        """
        This run in O(1)
        """

        return self.graph[envy_project]

    def is_sink(self, project: int) -> bool:
        """
        A project is sink if there is no outgoing edge
        """
        return len(self.graph[project]) == 0

    def is_source(self, project: int) -> bool:
        """
        A project is source if there is no incoming edge
        """
        return all([project not in targets for targets in self.graph.values()])

    def update_envy_graph(
        self, project_id: int, allocation: Dict[int, List[int]]
    ) -> None:
        team = self.project_id_traces.get(project_id)
        new_utility_value = sum(
            [
                self.utility_function(self.student_id_traces.get(s), team.to_shell())
                for s in allocation[project_id]
            ]
        )
        self.additive_utilities[project_id] = new_utility_value

        updated_utility = self.additive_utilities[project_id]
        for other_project_id in self.additive_utilities.keys():
            if project_id == other_project_id:
                continue

            other_team = self.project_id_traces.get(other_project_id)
            other_project_utilities_with_curr_project_allocation = sum(
                [
                    self.utility_function(
                        self.student_id_traces.get(s), other_team.to_shell()
                    )
                    for s in allocation[project_id]
                ]
            )
            # In case utility increases, no loger envy with some and some will start envy
            if updated_utility > other_project_utilities_with_curr_project_allocation:
                self.remove_edge(project_id, other_project_id)
                self.add_edge(other_project_id, project_id)

            # In case utility decreases, will start envy with more and some will stop envying
            if updated_utility < other_project_utilities_with_curr_project_allocation:
                self.add_edge(project_id, other_project_id)
                self.remove_edge(other_project_id, project_id)

            # In case utility is equal to other, noone will envy
            if updated_utility == other_project_utilities_with_curr_project_allocation:
                self.remove_edge(project_id, other_project_id)
                self.remove_edge(other_project_id, project_id)

    def get_all_directed_cycles(self) -> List[List[int]]:
        visited = set([])
        cycles: List[List[int]] = []

        for start_node in self.graph:
            node_exists_in_cycle = any([start_node in cycle for cycle in cycles])
            if node_exists_in_cycle:
                continue
            local_cycles = []
            self._dfs(start_node, visited, [], local_cycles)
            if len(local_cycles) > 0:
                cycles.extend(local_cycles)

        return cycles

    def _dfs(
        self, node: int, visited: Set[int], path: List[int], cycles: List[List[int]]
    ):
        if node in path:
            cycles.append(path[path.index(node) :])
            return

        if node not in visited:
            visited.add(node)
            path.append(node)
            for neighbor in self.get_envy_targets(node):
                self._dfs(neighbor, visited, path, cycles)
            path.pop()
            visited.remove(node)
