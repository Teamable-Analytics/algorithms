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
from api.ai.interfaces.algorithm_options import GeneralizedEnvyGraphAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.student import Student
from api.models.team import Team, TeamShell
from api.models.team_set import TeamSet


class GeneralizedEnvyGraphAlgorithm(Algorithm):
    """
    Generalized Envy Graph Algorithm
    """

    envy_graph: EnvyGraph
    trace_dictionary: Dict[int, Student]

    algorithm_run_time: float

    def __init__(
        self,
        algorithm_options: GeneralizedEnvyGraphAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
    ):
        super().__init__(algorithm_options, team_generation_options)

        self.allocation: Dict[int, List[int]] = {}
        self.utilities: Dict[int, Dict[int, int]] = {}
        self.project_ids_to_projects = {team.project_id: team for team in self.teams}
        self.utility_function = algorithm_options.utility_function

    def prepare(self, students: List[Student]) -> None:
        self.utilities = self._calculate_utilities(
            students=students,
            utility_function=self.utility_function,
        )

    def _calculate_utilities(
        self,
        students: List[Student],
        utility_function: Callable[[Student, TeamShell], float],
    ) -> Dict[int, Dict[int, float]]:
        utilities: Dict[int, Dict[int, float]] = {
            team.project_id: {} for team in self.teams
        }

        for team in self.teams:
            for student in students:
                project_id = team.project_id
                utilities[project_id][student.id] = utility_function(
                    student, team.to_shell()
                )

        return utilities

    def _get_team_with_positive_utilities(self, student: Student) -> List[Team]:
        """
        This run in O(N)
        """
        return [
            team
            for team in self.teams
            if self.utilities[team.project_id][student.id] >= 0
        ]

    def _construct_team_from_allocation(self) -> TeamSet:
        """
        This run in O(N*M)
        """
        new_team_set = TeamSet()
        for index, alloc_items in enumerate(self.allocation.items()):
            project_id, student_ids = alloc_items
            new_team = Team(
                _id=index + 1,
                students=[
                    self.trace_dictionary.get(student_id) for student_id in student_ids
                ],
                requirements=self.project_ids_to_projects.get(project_id).requirements,
            )
            new_team_set.teams.append(new_team)

        return new_team_set

    def generate(self, students: List[Student]) -> TeamSet:
        self.envy_graph = EnvyGraph(self.teams, students, self.utility_function)
        self.allocation: Dict[int, List[int]] = {
            team.project_id: [] for team in self.teams
        }
        self.trace_dictionary = {student.id: student for student in students}

        i_star: int = -1
        for student in students:
            positive_utilities = self._get_team_with_positive_utilities(student)
            if len(positive_utilities) != 0:
                for project in positive_utilities:
                    if self.envy_graph.is_source(project.id):
                        i_star = project.id
                        break
            else:
                for team in self.teams:
                    if self.envy_graph.is_sink(team.project_id):
                        i_star = team.project_id
                        break

            if i_star == -1:
                raise ValueError("No i_star found")

            self.allocation[i_star].append(student.id)
            self.envy_graph.update_envy_graph(i_star, self.allocation)

            while True:
                all_directed_cycles = self.envy_graph.get_all_directed_cycles()
                if len(all_directed_cycles) == 0:
                    break

                cycle = all_directed_cycles[0]
                last_cycle_allocation = self.allocation[cycle[-1]]
                for i in range(len(cycle)):
                    project_id = cycle[i]
                    if i < len(cycle) - 1:
                        next_project_id_allocation = self.allocation[cycle[i + 1]]
                    else:
                        next_project_id_allocation = last_cycle_allocation

                    self.allocation[project_id] = next_project_id_allocation
                    self.envy_graph.update_envy_graph(project_id, self.allocation)

        return self._construct_team_from_allocation()
