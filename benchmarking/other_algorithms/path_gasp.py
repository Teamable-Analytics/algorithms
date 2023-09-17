import math
import time
from typing import List, Set

from benchmarking.data.interfaces import MockStudentProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
from benchmarking.evaluations.scenarios.concentrate_all_attributes import ConcentrateAllAttributes
from benchmarking.simulation.simulation import Simulation

from models.enums import ScenarioAttribute, Gender, Race
from models.student import Student, StudentEncoder

from itertools import combinations
import json

def generate_team_arrangements(students: List[Student], team_size: int) -> List[List[List[Student]]]:
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

    def recursive_generate(current_arrangement: List[List[int]], students_used: Set[int]):
        """
        Args:
            current_arrangement: The team we are constructing
            students_used: A set of students who already in current_arrangement
        """
        if len(students) == len(students_used):
            results.add(tuple(sorted(current_arrangement)))  # Add the sorted tuple to filter duplicates
        else:
            for team in team_combinations:
                if all(student not in students_used for student in team):
                    new_arrangement = current_arrangement + [team]
                    new_student_used = students_used.union(team)
                    recursive_generate(new_arrangement, new_student_used)

    recursive_generate([], set())

    # map back to students
    real_results: List[List[List[Student]]] = []
    for arrangement in results:
        team_list = []
        for team in arrangement:
            student_list: List[Student] = [student_id_map.get(student_id) for student_id in team]
            team_list.append(student_list)

        real_results.append(team_list)

    return real_results


def calculate_student_well_being_score(student: Student, project: int) -> float:
    if project not in student.preferences:
        return 0

    inverted_score = student.preferences.index(project)
    score = len(student.preferences) - inverted_score
    return score


def calculate_teams_well_being_score(teams: List[List[Student]], project_assignment: List[int]) -> float:
    all_teams_well_being_score = 0

    for team, project in zip(teams, project_assignment):
        team_well_being_score = 0
        for student in team:
            team_well_being_score += calculate_student_well_being_score(student, project)

        all_teams_well_being_score += team_well_being_score

    return all_teams_well_being_score


def run_pathgasp(sim: Simulation, team_size: int):
    # find all mutations of teams
    all_students = sim.student_provider.get()
    all_teams_arrangements = generate_team_arrangements(all_students, team_size)

    # find all mutations of projects
    all_projects_arrangements: List[List[int]] = list(map(list, combinations(sim.project_list, number_of_teams)))

    max_well_being_score = 0
    ideal_arrangement = None
    cnt = 0
    for arrangement in all_teams_arrangements:
        for projects_arrangement in all_projects_arrangements:
            well_being_score = calculate_teams_well_being_score(arrangement, projects_arrangement)
            if well_being_score > max_well_being_score:
                max_well_being_score = well_being_score
                ideal_arrangement = arrangement
                print(f"Mutation #{cnt}, score: {well_being_score}, teams: " +
                      f"{json.dumps(arrangement, cls=StudentEncoder)}")
            cnt += 1

    return ideal_arrangement


CLASS_SIZES = [8, 12, 20, 40, 100]
# CLASS_SIZES = [8]
TEAM_SIZE = 4
MAX_NUM_PROJECT_PREFERENCES = 3

for class_size in CLASS_SIZES:
    print(f"Class size: {class_size}")

    number_of_teams = math.ceil(class_size / 4)
    ratio_of_female_students = 0.5

    mock_num_projects = math.ceil(number_of_teams * 1.5)  # number of project should be more than number of teams
    mock_project_list = [i + 1 for i in range(mock_num_projects)]

    student_provider_settings = MockStudentProviderSettings(
        number_of_students=class_size,
        num_values_per_attribute={
            ScenarioAttribute.PROJECT_PREFERENCES.value: MAX_NUM_PROJECT_PREFERENCES,
        },
        project_list=mock_project_list,
    )

    print(
        f"Maximum well-being score possible: {student_provider_settings.number_of_students * MAX_NUM_PROJECT_PREFERENCES}")

    simulation = Simulation(
        num_teams=number_of_teams,
        scenario=ConcentrateAllAttributes(),
        student_provider=MockStudentProvider(student_provider_settings),
        metrics=[],
        project_list=mock_project_list,
    )

    # Run Path-GASP
    start_time = time.time()
    run_pathgasp(simulation, team_size=TEAM_SIZE)
    end_time = time.time()
    run_time = end_time - start_time
    print(f"Run time: {run_time:.4f} seconds")
    print()
