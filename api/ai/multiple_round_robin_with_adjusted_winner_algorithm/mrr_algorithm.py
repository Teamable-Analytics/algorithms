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
from heapq import heappush, heappop
from typing import List, Dict

from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_options import MultipleRoundRobinAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.multiple_round_robin_with_adjusted_winner_algorithm.custom_models import (
    TeamWithValues,
    StudentProjectValue,
)
from api.ai.multiple_round_robin_with_adjusted_winner_algorithm.utils import (
    is_ordered_envy_freeness_up_to_one_item,
)
from api.models.student import Student
from api.models.team_set import TeamSet


class MultipleRoundRobinWithAdjustedWinnerAlgorithm(Algorithm):
    def __init__(
        self,
        algorithm_options: MultipleRoundRobinAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        *args,
        **kwargs,
    ):
        super().__init__(algorithm_options, team_generation_options)
        self.utility_function = algorithm_options.utility_function

    def _get_values_heap(
        self, students: List[Student], teams_heap: List[TeamWithValues]
    ) -> Dict[int, List[StudentProjectValue]]:
        """
        Calculate each student values to each project and push them into a heap

        This run in O(N * H)
        """
        # Each project will have its own heap, showing how effective each student to that project
        values_heap: Dict[int, List[StudentProjectValue]] = {
            team.project_id: [] for team in teams_heap
        }
        for team in teams_heap:
            for student in students:
                new_value = StudentProjectValue(student, team, self.utility_function)
                heappush(values_heap[team.project_id], new_value)

        return values_heap

    def _has_student_with_positive_value(
        self, project_student_values: Dict[int, List[StudentProjectValue]]
    ) -> bool:
        """
        Check if there is a student with positive value to any project

        This run in O(N)
        """

        for project_id in project_student_values:
            if len(project_student_values[project_id]) == 0:
                continue
            largest_value = project_student_values[project_id][0]
            if largest_value.value > 0:
                return True

        return False

    def _has_dummy_student(
        self, project_student_values: Dict[int, List[StudentProjectValue]]
    ) -> bool:
        """
        Check if has dummy students

        This run in O(N)
        """
        for project_id in project_student_values:
            if len(project_student_values[project_id]) == 0:
                continue
            largest_value = project_student_values[project_id][0]
            if largest_value.student.id < 0:
                return True

        return False

    def _get_dummy_students(self, num_dummy_students: int) -> List[Student]:
        return [Student(_id=-index - 1) for index in range(num_dummy_students)]

    def _find_allocation_with_mrr(self, students: List[Student]) -> TeamSet:
        """
        This run in O(N * N * log(max(N, H)))
        with H is the number of students, N is the number of projects
        """

        # O(N)
        allocation_heap = []
        for team in enumerate(self.teams):
            heappush(allocation_heap, TeamWithValues(team, self.utility_function))

        # O(max(N, H))
        values_heap = self._get_values_heap(students, allocation_heap)

        assigned_students = set()
        num_students = len(students)
        # O(N * N * log(max(N, H)))
        while len(assigned_students) < num_students:
            if self._has_student_with_positive_value(values_heap):
                # Add dummy students
                num_dummy_students = len(allocation_heap) - (
                    len(students) % len(allocation_heap)
                )
                students.extend(self._get_dummy_students(num_dummy_students))

            updated_teams = []
            # O(N * log(max(N, H)))
            while len(allocation_heap) > 0:
                # O(log(max(N, H)))
                current_team = heappop(allocation_heap)

                current_heap = values_heap[current_team.project.id]

                # O(log(max(N, H)) * max(N, H))
                while (
                    len(current_heap) > 0
                    and current_heap[0].student.id in assigned_students
                ):
                    heappop(current_heap)

                if len(current_heap) == 0:
                    # O(log(max(N, H)))
                    heappush(updated_teams, current_team)
                    continue

                if not current_heap[0].value > 0 and current_heap[0].student.id < 0:
                    # O(log(max(N, H)))
                    dummy_student = heappop(current_heap)
                    current_team.add_student(dummy_student.student)
                else:
                    # O(log(max(N, H)))
                    student_project_value = heappop(current_heap)
                    current_team.add_student(student_project_value.student)
                    assigned_students.add(student_project_value.student.id)

                # O(log(max(N, H)))
                heappush(updated_teams, current_team)

            allocation_heap = updated_teams

        return TeamSet(teams=allocation_heap)

    def _adjust_allocation_with_adjusted_winner(self, team_set: TeamSet) -> TeamSet:
        """
        This run in O(N * N * H * H)
        """
        for team_i in team_set.teams:
            for team_j in team_set.teams:
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
        return team_set

    def generate(self, students: List[Student]) -> TeamSet:
        allocation = self._find_allocation_with_mrr(students)
        return self._adjust_allocation_with_adjusted_winner(allocation)
