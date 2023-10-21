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
from heapq import heappush
from typing import List, Dict, Set

from api.ai.new.double_round_robin_algorithm.custom_models import Utility
from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_options import DoubleRoundRobinAlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.new.double_round_robin_algorithm.utils import calculate_utilities
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class DoubleRoundRobinAlgorithm(Algorithm):
    def __init__(
        self,
        algorithm_options: DoubleRoundRobinAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
    ):
        super().__init__(algorithm_options, team_generation_options)

        self.projects = algorithm_options.projects

    def _round_robin(
        self,
        utilities: Dict[int, List[Utility]],
        num_students: int,
        allocation: Dict[int, List[Student]],
    ) -> Dict[int, List[Student]]:
        selected_students: Set[int] = set()
        while len(selected_students) < num_students:
            for project in self.projects:
                while (
                    len(utilities[project.id]) > 0
                    and utilities[project.id][0].student.id in selected_students
                ):
                    utilities[project.id].pop(0)

                if len(utilities[project.id]) == 0:
                    continue

                curr_utility = utilities[project.id].pop(0)
                allocation[project.id].append(curr_utility.student)
                selected_students.add(curr_utility.student.id)

        return allocation

    def generate(self, students: List[Student]) -> TeamSet:
        utilities = calculate_utilities(self.projects, students)

        positive_utilities: Dict[int, List[Utility]] = {
            project.id: [] for project in self.projects
        }
        positive_utility_students: Set[int] = set()
        negative_utilities: Dict[int, List[Utility]] = {
            project.id: [] for project in self.projects
        }
        negative_utility_students: Set[int] = set()

        for project in self.projects:
            for student in students:
                curr_utility = utilities[project.id][student.id]
                if curr_utility.value > 0:
                    heappush(positive_utilities[project.id], curr_utility)
                    positive_utility_students.add(student.id)
                else:
                    heappush(negative_utilities[project.id], curr_utility)
                    negative_utility_students.add(student.id)

        allocation: Dict[int, List[Student]] = {
            project.id: [] for project in self.projects
        }
        self._round_robin(
            negative_utilities, len(negative_utility_students), allocation
        )
        self._round_robin(
            positive_utilities, len(positive_utility_students), allocation
        )

        team_list: List[Team] = []
        idx = 0
        for project_id, students in allocation.items():
            team = Team(
                _id=idx,
                name="Team " + str(idx),
                students=students,
                project_id=project_id,
            )

            team_list.append(team)
            idx += 1

        return TeamSet(teams=team_list)
