from typing import List

from ai.new.interfaces.algorithm import ChooseAlgorithm
from models.student import Student
from models.team import Team
from models.team_set import TeamSet


def save_students_to_team(team: Team, students: List[Student]):
    for student in students:
        # todo: should undo any adds if either fail, like a db transaction
        team_added_student = team.add_student(student)
        student_added_team = student.add_team(team)
        if not team_added_student or not student_added_team:
            raise ValueError("Cannot add student to team or team cannot add student.")


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
