import math
import random
from typing import List, Dict, Tuple, Set

from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_options import GeneralizedEnvyGraphAlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.models.enums import (
    AlgorithmType,
    ScenarioAttribute,
    Gender,
    Race,
    RequirementOperator,
)
from api.models.project import Project, ProjectRequirement
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.graphing.graph_metadata import GraphData


def get_additive_utilities(
    students: List[Student], projects: List[Project]
) -> Dict[Tuple[int, int], int]:
    utilities: Dict[Tuple[int, int], int] = {}

    for project in projects:
        project_requirements = set(project.requirements)
        for student in students:
            student_utilities = 0
            student_attributes = student.attributes
            for attribute_id, attribute_values in student_attributes.items():
                if attribute_id in project_requirements:
                    student_utilities += sum(
                        [
                            1
                            for attribute_value in attribute_values
                            if attribute_value > 0
                        ]
                    )
                else:
                    student_utilities -= 1

            utilities[(project.id, student.id)] = student_utilities

    return utilities


class EnvyGraph:
    def __init__(self, students: List[Student]) -> None:
        """
        Initalize an envy graph

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

    def get_all_cycles(self) -> List[List[int]]:
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

    def draw(self) -> None:
        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()
        G.add_nodes_from(self.graph.keys())
        for source, targets in self.graph.items():
            for target in targets:
                G.add_edge(source, target)

        nx.draw(G, with_labels=True)
        plt.show()


def requirement_met_by_student(
    requirement: ProjectRequirement, student: Student
) -> bool:
    is_met = False
    for value in student.attributes.get(requirement.attribute):
        if requirement.operator == RequirementOperator.LESS_THAN:
            is_met |= value < requirement.value
        elif requirement.operator == RequirementOperator.MORE_THAN:
            is_met |= value > requirement.value
        else:  # default case is 'exactly'
            is_met |= value == requirement.value
    return is_met


class GEGAlgorithm(Algorithm):
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
        projects: List[Project],
    ):
        super().__init__(algorithm_options, team_generation_options)

        self.allocation: Dict[int, List[int]] = {}
        self.utilities: Dict[Tuple[int, int], int] = {}
        self.projects: List[Project] = projects

    def _randomize_utilities(
        self, students: List[Student]
    ) -> Dict[Tuple[int, int], int]:
        utilities: Dict[Tuple[int, int], int] = {}

        for project in self.projects:
            for student in students:
                utilities[(project.id, student.id)] = random.randint(-5, 5)

        return utilities

    def _get_N_plus(self, projects: List[Project], student: Student) -> List[Project]:
        """
        This run in O(N)
        """
        return [
            project
            for project in projects
            if self.utilities.get((project.id, student.id)) >= 0
        ]

    def construct_team_from_allocation(self) -> TeamSet:
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
            )
            new_team_set.teams.append(new_team)

        return new_team_set

    def generate(self, students: List[Student]) -> TeamSet:
        self.envy_graph = EnvyGraph(students)
        self.utilities = self._randomize_utilities(students)
        self.allocation: Dict[int, List[int]] = {
            project.id: [] for project in self.projects
        }
        self.trace_dictionary = {student.id: student for student in students}

        i_star: int = -1
        for student in students:
            positive_utilities = self._get_N_plus(self.projects, student)
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
            self.envy_graph.update_envy_graph(
                i_star, self.utilities.get((i_star, student.id))
            )

            # While G(pi) contains directed cycle C do
            # allocation_C = pi(i) if i not in C else pi(i_j+1) if i == i_j in C
            C = self.envy_graph.get_all_cycles()
            while len(C) > 0:
                for cycle in C:
                    allocation_C = []
                    for i in cycle:
                        if i in self.allocation:
                            allocation_C.append(self.allocation[i])
                            self.envy_graph.update_envy_graph(
                                i, self.utilities.get((i, student.id))
                            )
                        else:
                            i_j = cycle.index(i)
                            allocation_C.append(self.allocation[i_j + 1])
                            self.envy_graph.update_envy_graph(
                                i_j + 1, self.utilities.get((i_j + 1, student.id))
                            )

                    # Find the student with the lowest utility in the cycle

        return self.construct_team_from_allocation()


if __name__ == "__main__":
    CLASS_SIZES = [i for i in range(8, 1201, 4)]
    TEAM_SIZE = 4
    MAX_NUM_PROJECT_PREFERENCES = 3

    # Graph variables
    graph_data_dict: Dict[AlgorithmType, GraphData] = {}

    for class_size in CLASS_SIZES:
        print(f"Class size: {class_size}")

        number_of_teams = math.ceil(class_size / 4)
        ratio_of_female_students = 0.5

        mock_num_projects = math.ceil(
            number_of_teams * 1.5
        )  # number of project should be more than number of teams
        mock_project_list = [i + 1 for i in range(mock_num_projects)]

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            num_values_per_attribute={
                ScenarioAttribute.PROJECT_PREFERENCES.value: MAX_NUM_PROJECT_PREFERENCES,
            },
            attribute_ranges={
                ScenarioAttribute.AGE.value: list(range(20, 24)),
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 1 - ratio_of_female_students),
                    (Gender.FEMALE, ratio_of_female_students),
                ],
                ScenarioAttribute.GPA.value: list(range(60, 100)),
                ScenarioAttribute.RACE.value: list(range(len(Race))),
                ScenarioAttribute.MAJOR.value: list(range(1, 4)),
                ScenarioAttribute.YEAR_LEVEL.value: list(range(3, 5)),
                ScenarioAttribute.PROJECT_PREFERENCES.value: mock_project_list,
            },
        )

        student_provider = MockStudentProvider(student_provider_settings)

        projects = []
        for proj_id in mock_project_list:
            proj_requirements = []
            random_attributes = random.sample(range(1, 7), 4)
            for attribute in random_attributes:
                if attribute == ScenarioAttribute.PROJECT_PREFERENCES:
                    continue

                attribute_range = student_provider_settings.attribute_ranges[attribute]
                random_attribute_values = random.sample(
                    attribute_range,
                    MAX_NUM_PROJECT_PREFERENCES
                    if len(attribute_range) > MAX_NUM_PROJECT_PREFERENCES
                    else 1,
                )
                random_operator = random.choice(["exactly", "less than", "more than"])

                proj_requirements.append(
                    ProjectRequirement(
                        attribute, random_operator, random_attribute_values
                    )
                )

            projects.append(Project(proj_id, requirements=proj_requirements))

        geg_algorithm = GEGAlgorithm(
            GeneralizedEnvyGraphAlgorithmOptions(), None, projects
        )
        team_set = geg_algorithm.generate(student_provider.get())

        # Print team set
        for team in team_set.teams:
            team_str = ""
            for people in team.students:
                team_str += f"{people.id} "
            print(team_str)
            print("-----")
