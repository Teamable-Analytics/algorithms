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
        vertices = [team.id for team in teams]
        self.graph: Dict[int, Set[int]] = {vertex: set([]) for vertex in vertices}
        self.additive_utilities: Dict[int, int] = {vertex: 0 for vertex in vertices}
        self.team_id_traces: Dict[int, Team] = {t.id: t for t in teams}
        self.student_id_traces: Dict[int, Student] = {s.id: s for s in students}
        self.utility_function = utility_function

    def add_edge(self, envy_team_id: int, other_team_id: int) -> None:
        self.graph[envy_team_id].add(other_team_id)

    def remove_edge(self, no_loger_envy_team_id: int, other_team_id: int) -> None:
        if other_team_id in self.graph[no_loger_envy_team_id]:
            self.graph[no_loger_envy_team_id].remove(other_team_id)

    def get_envy_targets(self, envy_team_id: int) -> Set[int]:
        return self.graph[envy_team_id]

    def is_sink(self, team_id: int) -> bool:
        """
        A node is sink if there is no outgoing edge
        """
        return len(self.graph[team_id]) == 0

    def is_source(self, team_id: int) -> bool:
        """
        A node is source if there is no incoming edge
        """
        return all([team_id not in targets for targets in self.graph.values()])

    def update_envy_graph(self, team_id: int, allocation: Dict[int, List[int]]) -> None:
        team = self.team_id_traces.get(team_id)
        new_utility_value = sum(
            [
                self.utility_function(self.student_id_traces.get(s), team.to_shell())
                for s in allocation[team_id]
            ]
        )
        self.additive_utilities[team_id] = new_utility_value

        updated_utility = self.additive_utilities[team_id]
        for other_team_id in self.additive_utilities.keys():
            if team_id == other_team_id:
                continue

            other_team = self.team_id_traces.get(other_team_id)
            other_team_utility_with_current_team_allocation = sum(
                [
                    self.utility_function(
                        self.student_id_traces.get(s), other_team.to_shell()
                    )
                    for s in allocation[team_id]
                ]
            )
            # In case utility increases, no loger envy with some and some will start envy
            if updated_utility > other_team_utility_with_current_team_allocation:
                self.remove_edge(team_id, other_team_id)
                self.add_edge(other_team_id, team_id)

            # In case utility decreases, will start envy with more and some will stop envying
            if updated_utility < other_team_utility_with_current_team_allocation:
                self.add_edge(team_id, other_team_id)
                self.remove_edge(other_team_id, team_id)

            # In case utility is equal to other, noone will envy
            if updated_utility == other_team_utility_with_current_team_allocation:
                self.remove_edge(team_id, other_team_id)
                self.remove_edge(other_team_id, team_id)

    def get_all_directed_cycles(self) -> List[List[int]]:
        visited = set()
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

    def has_cycle(self) -> bool:
        return len(self.get_all_directed_cycles()) > 0

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
