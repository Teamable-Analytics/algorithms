from typing import Callable, List

from api.models.student import Student
from api.models.team import TeamShell, Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class ProportionalityUpToOneItem(TeamSetMetric):
    def __init__(
            self,
            calculate_utilities: Callable[[List[Student], TeamShell], float],
            *args,
            **kwargs
    ):
        super().__init__(theoretical_range=(0, 1), *args, **kwargs)
        self.calculate_utilities = calculate_utilities

    def calculate(self, team_set: TeamSet) -> float:
        all_students = [student for team in team_set.teams for student in team.students]

        return (
                self._is_proportional(team_set, all_students)
                or self._is_proportional_with_one_extra_student(team_set, all_students)
                or self._is_proportional_with_one_less_student(team_set, all_students)
        )

    def _is_proportional(self, team_set: TeamSet, all_students: List[Student]) -> bool:
        return all(
            [
                self._is_team_proportional(team, all_students, team_set.num_teams)
                for team in team_set.teams
            ]
        )

    def _is_proportional_with_one_extra_student(
            self, team_set: TeamSet, all_students: List[Student]
    ) -> bool:
        for team in team_set.teams:
            students_in_team = set([student.id for student in team.students])

            is_new_team_proportional = any(
                self._is_team_proportional(
                    Team(
                        _id=team.id,
                        students=team.students + [student],
                        project_id=team.project_id,
                        requirements=team.requirements,
                    ),
                    all_students,
                    team_set.num_teams,
                )
                for student in all_students
                if student.id not in students_in_team
            )

            if not is_new_team_proportional:
                return False

        return True

    def _is_proportional_with_one_less_student(
            self, team_set: TeamSet, all_students: List[Student]
    ) -> bool:
        for team in team_set.teams:
            is_new_team_proportional = any(
                [
                    self._is_team_proportional(
                        Team(
                            _id=team.id,
                            students=[
                                student_in_team
                                for student_in_team in team.students
                                if student_in_team.id != student.id
                            ],
                            project_id=team.project_id,
                            requirements=team.requirements,
                        ),
                        all_students,
                        team_set.num_teams,
                    )
                    for student in team.students
                ]
            )

            if not is_new_team_proportional:
                return False

        return True

    def _is_team_proportional(
            self, team: Team, all_students: List[Student], num_teams: int
    ) -> bool:
        class_utility = self.calculate_utilities(all_students, team.to_shell())
        team.utility = self.calculate_utilities(team.students, team.to_shell())

        expected_team_utility = class_utility / float(num_teams)
        return team.utility >= expected_team_utility
