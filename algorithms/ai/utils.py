from typing import List

from algorithms.ai.interfaces.algorithm import ChooseAlgorithm
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet


def save_students_to_team(team: Team, students: List[Student]):
    for student in students:
        # todo: should undo any adds if either fail, like a db transaction
        team.add_student(student)
        student.add_team(team)


def generate_with_choose(
    algorithm: ChooseAlgorithm, students: List[Student], teams: List[Team]
) -> TeamSet:
    while True:
        available_teams = algorithm.get_available_teams(teams)
        remaining_students = algorithm.get_remaining_students(students)
        team, student = algorithm.choose(available_teams, remaining_students)
        if not team or not student:
            break
        save_students_to_team(team, [student])
    return TeamSet(teams=teams)
