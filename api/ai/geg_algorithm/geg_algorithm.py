"""
Generalized Envy Graph Algorithm

Initialize an allocation pi where all teams are empty
for each student s ∈ S:
    pos_projects = projects with positive utilities for s
    if pos_projects is not empty:
        Choose a "source" project i_star from the graph G(pi) induced bt pos_projects
    else:
        Choose a "sink" project i_star from the graph G(pi)

    Add s to team i_star

    While G(pi) contains directed cycle C do
        allocation_C = pi(i) if i not in C else pi(i_j+1) if i == i_j in C
"""
from typing import List, Dict, Callable

from api.ai.geg_algorithm.envy_graph import EnvyGraph
from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_config import GeneralizedEnvyGraphAlgorithmConfig
from api.ai.interfaces.algorithm_options import GeneralizedEnvyGraphAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.dataclasses.student import Student
from api.dataclasses.team import Team, TeamShell
from api.dataclasses.team_set import TeamSet


class GeneralizedEnvyGraphAlgorithm(Algorithm):
    """
    Generalized Envy Graph Algorithm
    """

    envy_graph: EnvyGraph
    allocation: Dict[int, List[Student]]

    def __init__(
        self,
        algorithm_options: GeneralizedEnvyGraphAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        algorithm_config: GeneralizedEnvyGraphAlgorithmConfig,
    ):
        super().__init__(algorithm_options, team_generation_options)

        self.allocation = {}
        self.utilities = {team.id: {} for team in self.teams}

        self.team_id_to_team = {team.id: team for team in self.teams}
        self.utility_function = algorithm_config.utility_function

    def prepare(self, students: List[Student]) -> None:
        for team in self.teams:
            for student in students:
                self.utilities[team.id][student.id] = self.utility_function(
                    student, team.to_shell()
                )

    def _calculate_utility(
        self,
        students: List[Student],
        team: Team,
    ) -> float:
        """
        Calculate the utilities given a list of students and teams
        """
        return sum(
            [self.utility_function(student, team.to_shell()) for student in students]
        )

    def _calculate_marginal_utility(self, student: Student, team: Team) -> float:
        original_utility = self._calculate_utility(self.allocation[team.id], team)
        union_utility = self._calculate_utility(
            self.allocation[team.id] + [student], team
        )

        return union_utility - original_utility

    def _get_team_with_positive_marginal_utilities(
        self, student: Student
    ) -> List[Team]:
        return [
            team
            for team in self.teams
            if self._calculate_marginal_utility(student, team) >= 0
        ]

    def _get_source(self, teams: List[Team]) -> int:
        for team in teams:
            if self.envy_graph.is_source(team.id):
                return team.id

    def _get_sink(self, teams: List[Team]) -> int:
        for team in teams:
            if self.envy_graph.is_sink(team.id):
                return team.id

    def _exchange_over_cycle(self, cycle: List[int]):
        first_allocation = self.allocation[cycle[0]]

        for i in range(len(cycle) - 1):
            self.allocation[cycle[i]] = self.allocation[cycle[i + 1]]

        self.allocation[cycle[-1]] = first_allocation

    def _construct_team_set_from_allocation(self) -> TeamSet:
        teams = []
        for team_id, students in self.allocation.items():
            if len(students) == 0:
                continue
            team = self.team_id_to_team[team_id]
            team.students = students
            teams.append(team)

        return TeamSet(teams=teams)

    def generate(self, students: List[Student]) -> TeamSet:
        self.envy_graph = EnvyGraph(self.teams, students, self.utility_function)
        self.allocation = {team.id: [] for team in self.teams}

        for student in students:
            positive_marginal_utility_teams = (
                self._get_team_with_positive_marginal_utilities(student)
            )
            if len(positive_marginal_utility_teams) > 0:
                i_star = self._get_source(positive_marginal_utility_teams)
            else:
                i_star = self._get_sink(self.teams)

            if i_star is None:
                continue

            self.allocation[i_star].append(student)

            envy_graph_cycles = self.envy_graph.get_all_directed_cycles()
            while len(envy_graph_cycles) > 0:
                self._exchange_over_cycle(envy_graph_cycles.pop())
                envy_graph_cycles = self.envy_graph.get_all_directed_cycles()

        return self._construct_team_set_from_allocation()
