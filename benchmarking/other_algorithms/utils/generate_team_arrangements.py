from itertools import combinations
from typing import List, Set

from models.student import Student


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