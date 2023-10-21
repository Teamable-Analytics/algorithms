from typing import List

from api.ai.new.interfaces.algorithm import ChooseAlgorithm
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


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
