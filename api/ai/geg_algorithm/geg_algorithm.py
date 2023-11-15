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
from typing import List, Dict

from api.ai.geg_algorithm.envy_graph import EnvyGraph
from api.ai.geg_algorithm.utils import calculate_value
from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_options import GeneralizedEnvyGraphAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.project import Project
from api.models.student import Student
from api.models.team import Team
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
        self.projects: List[Project] = algorithm_options.projects
        self.project_ids_to_projects = {
            project.id: project for project in self.projects
        }

    def _calculate_utilities(
        self, students: List[Student]
    ) -> Dict[int, Dict[int, int]]:
        utilities: Dict[int, Dict[int, int]] = {}

        for project in self.projects:
            for student in students:
                if project.id not in utilities:
                    utilities[project.id] = {}
                utilities[project.id][student.id] = calculate_value(
                    student, project.requirements
                )

        return utilities

    def _get_projects_with_positive_utilities(
        self, projects: List[Project], student: Student
    ) -> List[Project]:
        """
        This run in O(N)
        """
        return [
            project
            for project in projects
            if self.utilities[project.id][student.id] >= 0
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
        self.envy_graph = EnvyGraph(self.projects, students)
        self.utilities = self._calculate_utilities(students)
        self.allocation: Dict[int, List[int]] = {
            project.id: [] for project in self.projects
        }
        self.trace_dictionary = {student.id: student for student in students}

        i_star: int = -1
        for student in students:
            positive_utilities = self._get_projects_with_positive_utilities(
                self.projects, student
            )
            if len(positive_utilities) != 0:
                for project in positive_utilities:
                    if self.envy_graph.is_source(project.id):
                        i_star = project.id
                        break
            else:
                for project in self.projects:
                    if self.envy_graph.is_sink(project.id):
                        i_star = project.id
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
