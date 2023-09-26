import math
import time
from collections import defaultdict
from typing import List, Set, Dict

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.graphing.graph_metadata import GraphData
from benchmarking.evaluations.graphing.line_graph import line_graph
from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
from benchmarking.evaluations.scenarios.concentrate_all_attributes import (
    ConcentrateAllAttributes,
)
from benchmarking.simulation.simulation import Simulation, RunOutput

from models.enums import ScenarioAttribute, AlgorithmType
from models.student import Student, StudentEncoder

from itertools import combinations
import json


def generate_team_arrangements(
    students: List[Student], team_size: int
) -> List[List[List[Student]]]:
    """
    Get all possible team arrangements

    Runtime:
        O( (N choose k) * N )
            with N = len(students) and K = team_size
    """
    if len(students) % team_size != 0:
        raise ValueError("Number of people must be divisible by team size")

    student_ids = [student.id for student in students]
    student_id_map = {student.id: student for student in students}
    team_combinations = list(combinations(student_ids, team_size))
    results = set()  # this result only contains student ids

    def recursive_generate(
        current_arrangement: List[List[int]], students_used: Set[int]
    ):
        """
        Args:
            current_arrangement: The team we are constructing
            students_used: A set of students who already in current_arrangement
        """
        if len(students) == len(students_used):
            results.add(
                tuple(sorted(current_arrangement))
            )  # Add the sorted tuple to filter duplicates
        else:
            for team_combination in team_combinations:
                if all(student not in students_used for student in team_combination):
                    new_arrangement = current_arrangement + [team_combination]
                    new_student_used = students_used.union(team_combination)
                    recursive_generate(new_arrangement, new_student_used)

    recursive_generate([], set())

    # map back to students
    real_results: List[List[List[Student]]] = []
    for arrangement in results:
        team_list = []
        for team in arrangement:
            student_list: List[Student] = [
                student_id_map.get(student_id) for student_id in team
            ]
            team_list.append(student_list)

        real_results.append(team_list)

    return real_results


def calculate_student_well_being_score(student: Student, project: int) -> float:
    if project not in student.preferences:
        return 0

    inverted_score = student.preferences.index(project)
    score = len(student.preferences) - inverted_score
    return score


def calculate_teams_well_being_score(
    teams: List[List[Student]], project_assignment: List[int]
) -> float:
    all_teams_well_being_score = 0

    for team, project in zip(teams, project_assignment):
        team_well_being_score = 0
        for student in team:
            team_well_being_score += calculate_student_well_being_score(
                student, project
            )

        all_teams_well_being_score += team_well_being_score

    return all_teams_well_being_score


class PathGaspSimulation(Simulation):
    def run(self, team_size: int) -> RunOutput:
        # find all mutations of teams
        all_students = self.student_provider.get()

        all_teams_arrangements = generate_team_arrangements(all_students, team_size)
        attribute_ranges = self.student_provider.settings.attribute_ranges
        project_list = attribute_ranges.get(
            ScenarioAttribute.PROJECT_PREFERENCES.value, None
        )

        # find all mutations of projects
        all_projects_arrangements: List[List[int]] = list(
            map(list, combinations(project_list, number_of_teams))
        )

        # Run algorithm
        start_time = time.time()
        max_well_being_score = 0
        ideal_arrangement = None
        cnt = 0
        for arrangement in all_teams_arrangements:
            for projects_arrangement in all_projects_arrangements:
                well_being_score = calculate_teams_well_being_score(
                    arrangement, projects_arrangement
                )
                if well_being_score > max_well_being_score:
                    max_well_being_score = well_being_score
                    ideal_arrangement = arrangement
                    print(
                        f"Mutation #{cnt}, score: {well_being_score}, teams: "
                        + f"{json.dumps(arrangement, indent=2, cls=StudentEncoder)}"
                    )
                cnt += 1

        end_time = time.time()
        self.run_outputs[AlgorithmType.PATH_GASP][Simulation.KEY_RUNTIMES] = [
            end_time - start_time
        ]

        # TODO: Metric evaluation using ideal_arrangement

        return self.run_outputs


if __name__ == "__main__":
    CLASS_SIZES = [8, 12, 16, 20, 24, 28, 32]
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
                ScenarioAttribute.PROJECT_PREFERENCES.value: mock_project_list
            },
        )

        print(
            f"Maximum well-being score possible: {student_provider_settings.number_of_students * MAX_NUM_PROJECT_PREFERENCES}"
        )

        simulation_outputs = PathGaspSimulation(
            num_teams=number_of_teams,
            scenario=ConcentrateAllAttributes(),
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
            title="Run PATH-GASP",
            data=list(graph_data_dict.values()),
            description=None,
            y_lim=None,
            x_lim=None,
        )
    )
