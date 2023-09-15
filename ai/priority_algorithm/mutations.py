import random

from models.student import Student
from models.team import Team
from models.team_set import TeamSet


def swap_student_between_teams(
        self,
        team1: Team,
        student_1: Student,
        team2: Team,
        student_2: Student,
):
    """
    Swaps students between teams, needs to use student not student_id
    TODO: Opey
    """
    team1.students.remove(student_1)
    team1.students.append(student_2)


def mutate_team_random(self, team_set: TeamSet) -> TeamSet:
    available_priority_teams = [
        priority_team
        for priority_team in team_set.priority_teams
        if not priority_team.team.is_locked
    ]
    try:
        team1, team2 = random.sample(available_priority_teams, 2)
        student_1: Student = random.choice(team1.students)
        student_2: Student = random.choice(team2.students)
        self.swap_student_between_teams(team1, student_1, team2, student_2)
    except ValueError:
        return team_set
    return team_set
