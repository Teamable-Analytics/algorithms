"""
N = list of projects
H = list of students
V = value function

while H is not empty:
    Order N by team value V(n) ascending (each project has 1 team)
    if ∃ student s ∈ H, project n ∈ N that u_n(s) > 0:
        add k dummy students h_k to H, that len(H) + k = a * len(N) with a is an arbitrary constant

    for n in N:
        if not ∃ project n ∈ N that V(n) > 0 and there is h_k ∈ H:
            h_k -> n.team
        else:
            student_max = argmax student s ∈ H of V(n with s)
            student_max -> n.team
            update V(n)
            Reorder N by team value V(n) ascending (each project has 1 team)
"""
import math
from heapq import heappush, nsmallest
import random
from typing import List, Dict

from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_options import MultipleRoundRobinAlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.models.enums import ScenarioAttribute, Gender, Race, AlgorithmType
from api.models.project import Project, ProjectRequirement
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider, MockStudentProviderSettings
from benchmarking.evaluations.graphing.graph_metadata import GraphData


def calculate_value(student: Student, requirements: List[ProjectRequirement]) -> int:
    return sum([
        1 if student.meets_requirement(requirement) else -1
        for requirement in requirements
    ])


class TeamWithValues(Team):
    project: Project

    def __init__(self, _id: int, project: Project):
        super().__init__(_id=_id)
        self.value = 0
        self.project = project

    def add_student(self, student: Student) -> bool:
        if super().add_student(student):
            self.value += calculate_value(student, self.project.requirements)
            return True
        return False

    def __lt__(self, other):
        return self.value < other.value


class StudentProjectValue:
    def __init__(self, student: Student, project: Project):
        self.student = student
        self.project = project
        self.value = 0 if student.id < 0 else calculate_value(student, project.requirements)

    def __lt__(self, other):
        # Redefine the less than operator to make it a max heap
        return self.value > other.value


class MultipleRoundRobinAlgorithm(Algorithm):
    def __init__(self,
                 algorithm_options: MultipleRoundRobinAlgorithmOptions,
                 team_generation_options: TeamGenerationOptions,
                 projects: List[Project]):
        super().__init__(algorithm_options, team_generation_options)
        self.projects = projects

    def _get_values_heap(self,
                         students: List[Student],
                         teams: List[TeamWithValues]) -> List[StudentProjectValue]:
        """
        Calculate each student values to each project and push them into a heap

        This run in O(N * H)
        """
        # (project_id, student_id) -> value
        values_heap: List[StudentProjectValue] = []
        for team in teams:
            project = team.project
            for student in students:
                new_node = StudentProjectValue(student, project)
                heappush(values_heap, new_node)

        return values_heap

    def _has_student_with_positive_value(self, project_student_values: List[StudentProjectValue]) -> bool:
        """
        Check if there is a student with positive value to any project
        """
        largest_value = nsmallest(1, project_student_values)[0]  # O(1)
        return largest_value.value > 0

    def _has_dummy_student(self, project_student_values: List[StudentProjectValue]) -> bool:
        """
        Check if there is a student with positive value to any project
        """
        largest_value = nsmallest(1, project_student_values)[0]  # O(1)
        return largest_value.student.id < 0

    def _get_dummy_students(self, num_dummy_students: int) -> List[Student]:
        return [Student(_id=-index - 1) for index in range(num_dummy_students)]

    def generate(self, students: List[Student]) -> TeamSet:
        teams = [TeamWithValues(idx, project) for idx, project in enumerate(self.projects)]  # O(N)

        values_heap = self._get_values_heap(students, teams)  # O(N * H)

        while len(values_heap) > 0:  # O(H)
            teams = sorted(teams)  # O(N * log(N))
            if self._has_student_with_positive_value(values_heap):
                # Add dummy students
                num_dummy_students = len(teams) - (len(students) % len(teams))
                students.extend(self._get_dummy_students(num_dummy_students))

            for team_idx in range(len(teams)):
                if not self._has_student_with_positive_value(values_heap) and self._has_dummy_student(values_heap):
                    dummy_student = values_heap.pop()
                    teams[team_idx].add_student(dummy_student.student)
                else:
                    student_project_value = values_heap.pop()
                    teams[team_idx].add_student(student_project_value.student)
                    # Reorder projects and set
                    teams = sorted(teams)  # O(N * log(N))
                    team_idx = 0
        return TeamSet(teams=teams)


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

        mrr_algorithm = MultipleRoundRobinAlgorithm(
            MultipleRoundRobinAlgorithmOptions(), None, projects
        )
        team_set = mrr_algorithm.generate(student_provider.get())

        # Print team set
        for team in team_set.teams:
            team_str = ""
            for people in team.students:
                team_str += f"{people.id} "
            print(team_str)
            print("-----")
