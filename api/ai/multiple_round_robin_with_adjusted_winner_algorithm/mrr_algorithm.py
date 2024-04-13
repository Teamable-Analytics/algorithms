"""
N = list of projects
H = list of students
V = value function

Find biased allocation using MRR
while H is not empty:
    Order N by team value V(n) ascending (each project has 1 team)
    if ∃ student s ∈ H, project n ∈ N that u_n(s) > 0:
        add k dummy students h_k to H, that len(H) + k = a * len(N) with a is an arbitrary constant

    for n in N:
        if not ∃ project n ∈ N that V(n) > 0 and there is h_k ∈ H:
            h_k -> n.team
        else:
            student_max = argmax student s ∈ H of V(n with s)
            student_max -> n.team
            update V(n)
            Reorder N by team value V(n) ascending (each project has 1 team)

Apply Adjusted Winner Algorithm to the found allocation
for team_i in N:
    for team_j in N:
        if team_i is not OEF1 w.r.t team_j:
            for student in team_j:
                if (team_i + student).value > team_i.value:
                    Assign student to team_i

"""
from typing import List

from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_config import MultipleRoundRobinAlgorithmConfig
from api.ai.interfaces.algorithm_options import MultipleRoundRobinAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.multiple_round_robin_with_adjusted_winner_algorithm.custom_dataclasses import (
    TeamWithValues,
)
from api.ai.multiple_round_robin_with_adjusted_winner_algorithm.utils import (
    is_ordered_envy_freeness_up_to_one_item,
)
from api.dataclasses.student import Student
from api.dataclasses.team import Team
from api.dataclasses.team_set import TeamSet


class MultipleRoundRobinWithAdjustedWinnerAlgorithm(Algorithm):
    def __init__(
        self,
        algorithm_options: MultipleRoundRobinAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        algorithm_config: MultipleRoundRobinAlgorithmConfig,
    ):
        super().__init__(algorithm_options, team_generation_options, algorithm_config)
        self.utility_function = algorithm_config.utility_function

    def generate(self, students: List[Student]) -> TeamSet:
        teams = [team for team in self._new_mrr(students) if len(team.students) > 0]
        return self._adjust_allocation_with_adjusted_winner(teams)

    def _is_there_a_student_with_positive_value_for_a_team(
        self, teams: List[TeamWithValues], students: List[Student]
    ) -> bool:
        for team in teams:
            for student in students:
                student_utility = self.utility_function(student, team.to_shell())
                if student_utility > 0:
                    return True
        return False

    def _is_there_no_student_with_positive_value_but_there_is_some_dummy_student(
        self, team: TeamWithValues, students: List[Student]
    ) -> bool:
        has_dummy_student = False
        for student in students:
            student_utility = self.utility_function(student, team.to_shell())
            if student_utility > 0:
                return False
            if student.id < 0:
                has_dummy_student = True
        return has_dummy_student

    def _add_dummy_till_number_of_students_is_multiple_of_number_of_teams(
        self, students: List[Student], num_teams: int
    ):
        i = 0
        while len(students) % num_teams != 0:
            i += 1
            dummy_student = Student(
                _id=-i,
                name="Dummy Student " + str(i),
                attributes={},
                relationships={},
            )
            students.append(dummy_student)

    def _add_dummy_student_to_team(self, team: TeamWithValues, students: List[Student]):
        for student in students:
            if student.id < 0:
                team.add_student(student)
                students.remove(student)
                return

    def _assign_highest_utility_student_to_team(
        self, team: TeamWithValues, students: List[Student]
    ):
        best_student: Student = students[0]

        for student in students[1:]:
            student_utility = self.utility_function(student, team.to_shell())
            best_student_utility = self.utility_function(best_student, team.to_shell())
            if student_utility > best_student_utility:
                best_student = student

        team.add_student(best_student)
        students.remove(best_student)

    def _new_mrr(self, students: List[Student]) -> List[Team]:
        teams = [TeamWithValues(team, self.utility_function) for team in self.teams]

        while len(students) > 0:
            teams.sort()
            if self._is_there_a_student_with_positive_value_for_a_team(teams, students):
                self._add_dummy_till_number_of_students_is_multiple_of_number_of_teams(
                    students, len(teams)
                )

            for team_idx in range(len(teams)):
                team = teams[team_idx]
                if self._is_there_no_student_with_positive_value_but_there_is_some_dummy_student(
                    team, students
                ):
                    self._add_dummy_student_to_team(team, students)
                else:
                    self._assign_highest_utility_student_to_team(team, students)
                    teams.sort()
                    team_idx = 0

        return teams

    def _adjust_allocation_with_adjusted_winner(self, teams: List[Team]) -> TeamSet:
        for team_i in teams:
            for team_j in teams:
                if team_i is team_j:
                    continue
                if is_ordered_envy_freeness_up_to_one_item(
                    team_i, team_j, self.utility_function
                ):
                    continue

                for student in team_j.students:
                    student_value_to_team_i = self.utility_function(
                        student, team_i.to_shell()
                    )
                    if student_value_to_team_i > 0:
                        team_i.add_student(student)
                        team_j.remove_student(student)
        return TeamSet(teams=teams)
