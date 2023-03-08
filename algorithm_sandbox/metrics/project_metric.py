from typing import List

from team_formation.app.team_generator.team import Team


def has_team_met_requirements(team):
    for req in team.requirements:
        f = False
        for stu in team.students:
            f |= team.requirement_met_by_student(req, stu)
        if not f:
            return 0
    return 1


def satisfied_requirements(team):
    ans = 0
    for req in team.requirements:
        f = False
        for stu in team.students:
            f |= team.requirement_met_by_student(req, stu)
        ans += f
    return ans


def get_project_metrics(teams: List[Team]):
    return {
        'S_T': sum([has_team_met_requirements(team) for team in teams]),
        'S_R': sum([satisfied_requirements(team) for team in teams]),
    }
