"""
Definition:
    N = list of agents. In this algorithm, we use the list of projects
    O = list of tasks that need to be allocated. In this algorithm, we use the students
    U = matrix of utilities, in this algorithm, we will calculate the usefulness of each student to the project.
        More specifically, each skill a student has that in project requirement (useful) will add 1 to their utility,
        and if their skill is not in project requirement (not useful), their utility will be decrease by 1.

    Step 0: Preparation
    - Calculate each student utility for each project and put it in U

    Step 1:
    - Split U into 2 matrix: 1 contains all positive utilities (U_plus) and 1 contains negative utilities (U_minus).

    Step 2:
    - If the length of U_minus is not divisible by length of N (n), add dummy student until it is.

    Step 3:
    - Go for the first round-robin sequence (from project 1 to n) in U_minus.

    Step 4:
    - Go for the second round-robin sequence (from project n to 1) in U_plus.
    - If no student available, add a dummy one instead.

    Step 5:
    - Remove all dummy student
    - Return the allocations
"""
import math
import time
from dataclasses import dataclass
import random
from typing import Dict, List, Tuple

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.scenarios.concentrate_multiple_attributes import ConcentrateMultipleAttributes
from benchmarking.other_algorithms.utils.generate_team_arrangements import generate_team_arrangements
from benchmarking.simulation.simulation import Simulation
from models.enums import ScenarioAttribute, AlgorithmType, Gender, Race

from models.project import ProjectRequirement
from models.student import Student
from old.team_formation.app.team_generator.algorithm.consts import REQUIREMENT_TYPES


@dataclass
class Project:
    id: int
    requirements: List[int]


def _calculate_utilities(projects: List[Project], students: List[Student]) -> Dict[Tuple[int, int], int]:
    utilities: Dict[Tuple[int, int], int] = {}

    for project in projects:
        project_requirements = set(project.requirements)
        for student in students:
            student_utilities = 0
            student_attributes = student.attributes
            for attribute_id, attribute_values in student_attributes.items():
                if attribute_id in project_requirements:
                    student_utilities += sum([1 for attribute_value in attribute_values if attribute_value > 0])
                else:
                    student_utilities -= 1

            utilities[(project.id, student.id)] = student_utilities

    return utilities


class DoubleRoundRobin(Simulation):
    def _generate_project_requirements(self) -> List[Project]:
        # For now, assuming each project has 4 requirements
        num_reqs_per_project = 4
        project_ids = self.student_provider.settings.attribute_ranges.get(
            ScenarioAttribute.PROJECT_PREFERENCES.value, []
        )
        projects = []
        all_attribute_requirements = list(ScenarioAttribute)
        for project_id in project_ids:
            projects.append(Project(
                id=project_id,
                requirements=list(
                    map(lambda x: x.value, random.sample(all_attribute_requirements, num_reqs_per_project)))
            ))
        return projects

    def run(self, team_size: int):
        ### Step 0
        # Student list
        O = self.student_provider.get()

        # Project list
        N: List[Project] = self._generate_project_requirements()

        # Utilities matrix
        U = _calculate_utilities(N, O)

        start_time = time.time()

        ### Step 1
        U_plus: Dict[Tuple[int, int], int] = {}
        U_minus: Dict[Tuple[int, int], int] = {}
        U_minus_items = set()
        U_plus_items = set()
        for n in N:
            for o in O:
                key = (n.id, o.id)
                utility = U.get(key)
                if utility is None:
                    raise ValueError(f"No utility value for project {n.id} and student {o.id}")
                if utility > 0:
                    U_plus[key] = utility
                    U_plus_items.add(o.id)
                else:
                    U_minus[key] = utility
                    U_minus_items.add(o.id)

        ### Step 2
        k = len(U_minus_items) % len(N)
        U_minus_items |= set([-i for i in range(1, k + 1)])  # Dummy student has negative id

        ### Step 3
        chosen = set()
        result: Dict[int, List[int]] = {}
        while len(chosen) < len(U_minus_items):
            for n in N:
                max_util = float('-inf')
                max_util_item = None
                for item_id in U_minus_items:
                    if item_id in chosen:
                        continue

                    utility = U_minus.get((n.id, item_id), 0)
                    if max_util < utility:
                        max_util_item = item_id
                        max_util = utility

                chosen.add(max_util_item)
                if n.id in result:
                    result[n.id].append(max_util_item)
                else:
                    result[n.id] = [max_util_item]


        ### Step 4
        chosen = set()
        while len(chosen) < len(U_plus_items):
            for n in N[::-1]:
                max_util = float('-inf')
                max_util_item = None
                for item_id in U_plus_items:
                    if item_id in chosen:
                        continue

                    utility = U_plus.get((n.id, item_id), 0)
                    if max_util < utility:
                        max_util_item = item_id
                        max_util = utility

                chosen.add(max_util_item)
                if n.id in result:
                    result[n.id].append(max_util_item)
                else:
                    result[n.id] = [max_util_item]


        ### Step 5
        for key, values in result.items():
            result[key] = [value for value in values if value is not None and value > 0]


        end_time = time.time()
        self.run_outputs[AlgorithmType.PATH_GASP][Simulation.KEY_RUNTIMES] = [
            end_time - start_time
        ]

        print(result)
        return self.run_outputs


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
                ScenarioAttribute.PROJECT_PREFERENCES.value: mock_project_list
            },
        )

        simulation_outputs = DoubleRoundRobin(
            num_teams=number_of_teams,
            scenario=ConcentrateMultipleAttributes(
                [
                    ScenarioAttribute.AGE,
                    ScenarioAttribute.GENDER,
                    ScenarioAttribute.GPA,
                    ScenarioAttribute.RACE,
                    ScenarioAttribute.MAJOR,
                    ScenarioAttribute.YEAR_LEVEL,
                ]
            ),
            student_provider=MockStudentProvider(student_provider_settings),
            metrics=[],
            algorithm_types=[AlgorithmType.PATH_GASP],
        ).run(team_size=TEAM_SIZE)


        average_runtimes = Simulation.average_metric(simulation_outputs, "runtimes")
        # Data processing for graph
        for algorithm_type, average_runtime in average_runtimes.items():
            if algorithm_type not in graph_data_dict:
                graph_data_dict[algorithm_type] = GraphData(
                    x_data=[class_size],
                    y_data=[average_runtime],
                    name=algorithm_type.value,
                )
            else:
                graph_data_dict[algorithm_type].x_data.append(class_size)
                graph_data_dict[algorithm_type].y_data.append(average_runtime)

    line_graph(
        LineGraphMetadata(
            x_label="Class size",
            y_label="Run time (seconds)",
            title="Run Double Round Robin",
            data=list(graph_data_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )