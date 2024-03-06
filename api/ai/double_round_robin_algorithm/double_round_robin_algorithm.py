"""
Definition:
    N = list of agents. In this algorithm, we use the list of projects
    O = list of tasks that need to be allocated. In this algorithm, we use the students
    U = matrix of utilities, in this algorithm, we will calculate the usefulness of each student to the project.
        More specifically, each skill a student has that in project requirement (useful) will add 1 to their utility,
        and if their skill is not in project requirement (not useful), their utility will be decrease by 1.

    Step 0: Preparation
    - Calculate each student utility for each project and put it in U

    Step 1:
    - Split U into 2 matrix: 1 contains all positive utilities (U_plus) and 1 contains negative utilities (U_minus).

    Step 2:
    - If the length of U_minus is not divisible by length of N (n), add dummy student until it is.

    Step 3:
    - Go for the first round-robin sequence (from project 1 to n) in U_minus.

    Step 4:
    - Go for the second round-robin sequence (from project n to 1) in U_plus.
    - If no student available, add a dummy one instead.

    Step 5:
    - Remove all dummy student
    - Return the allocations
"""
from typing import List, Dict, Set, Callable

from api.ai.double_round_robin_algorithm.custom_models import Utility
from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_config import DoubleRoundRobinAlgorithmConfig
from api.ai.interfaces.algorithm_options import DoubleRoundRobinAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.student import Student
from api.models.team import Team, TeamShell
from api.models.team_set import TeamSet


class DoubleRoundRobinAlgorithm(Algorithm):
    utilities: Dict[int, Dict[int, Utility]]

    def __init__(
        self,
        algorithm_options: DoubleRoundRobinAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        algorithm_config: DoubleRoundRobinAlgorithmConfig,
        *args,
        **kwargs,
    ):
        super().__init__(algorithm_options, team_generation_options)

        self.project_ids_tracer = {
            team.project_id: team_idx for team_idx, team in enumerate(self.teams)
        }
        self.utility_function = algorithm_config.utility_function

    def prepare(self, student: List[Student]) -> None:
        self.utilities = self._calculate_utilities(
            student, self.teams, self.utility_function
        )

    def _calculate_utilities(
        self,
        students: List[Student],
        teams: List[Team],
        utility_function: Callable[[Student, TeamShell], float],
    ) -> Dict[int, Dict[int, Utility]]:
        utilities = {team.project_id: {} for team in teams}
        for team in teams:
            for student in students:
                utilities[team.project_id][student.id] = Utility(
                    student=student,
                    project_id=team.project_id,
                    value=utility_function(student, team.to_shell()),
                )
        return utilities

    def _round_robin(
        self,
        utilities: Dict[int, List[Utility]],
        num_students: int,
        allocation: Dict[int, List[Student]],
        selected_students: Set[int],
        total_dummy_students: int = -1,
    ) -> Dict[int, List[Student]]:
        dummy_student_counter = 1

        while len(selected_students) < num_students:
            for team in self.teams:
                sorted_utilities_of_team = sorted(
                    utilities[team.project_id], reverse=True
                )

                while (
                    len(sorted_utilities_of_team) > 0
                    and sorted_utilities_of_team[0].student.id in selected_students
                ):
                    sorted_utilities_of_team.pop(0)
                    if len(sorted_utilities_of_team) == 0:
                        break

                if len(sorted_utilities_of_team) == 0:
                    continue

                added_dummy_student = (
                    sorted_utilities_of_team[0].value < 0
                    and dummy_student_counter < total_dummy_students
                )

                if added_dummy_student:
                    dummy_student_counter += 1
                else:
                    curr_utility = sorted_utilities_of_team.pop(0)
                    allocation[team.project_id].append(curr_utility.student)
                    selected_students.add(curr_utility.student.id)

        return allocation

    def generate(self, students: List[Student]) -> TeamSet:
        positive_utilities: Dict[int, List[Utility]] = {
            team.project_id: [] for team in self.teams
        }
        positive_utility_students: Set[int] = set()
        negative_utilities: Dict[int, List[Utility]] = {
            team.project_id: [] for team in self.teams
        }
        negative_utility_students: Set[int] = set()

        for team in self.teams:
            for student in students:
                curr_utility = self.utilities[team.project_id][student.id]
                if curr_utility.value > 0:
                    positive_utilities[team.project_id].append(curr_utility)
                    positive_utility_students.add(student.id)
                else:
                    negative_utilities[team.project_id].append(curr_utility)
                    negative_utility_students.add(student.id)

        # Add dummy students to negative utilities
        num_dummy_students = (
            len(self.teams) - len(negative_utility_students) % len(self.teams)
        ) % len(self.teams)

        selected_students: Set[int] = set()
        allocation: Dict[int, List[Student]] = {
            team.project_id: [] for team in self.teams
        }

        self._round_robin(
            negative_utilities,
            len(negative_utility_students),
            allocation,
            selected_students,
            num_dummy_students,
        )

        self._round_robin(
            positive_utilities,
            len(positive_utility_students),
            allocation,
            selected_students,
        )

        for project_id, students in allocation.items():
            team_idx = self.project_ids_tracer[project_id]
            self.teams[team_idx].students = students
            self.teams[team_idx].is_locked = True

        return TeamSet(teams=[team for team in self.teams if len(team.students) > 0])
