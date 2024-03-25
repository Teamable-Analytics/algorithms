import unittest
from typing import List, Dict, Tuple

from schema import Schema

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations import utils
from api.ai.priority_algorithm.mutations.robinhood import RobinhoodMutation
from api.ai.priority_algorithm.mutations.robinhood_holistic import (
    RobinhoodHolisticMutation,
)
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student
from api.dataclasses.team import Team, TeamShell


class StudentListPriority(Priority):
    """
    A custom priority for this test.
    It wants all students in list to be in a team
    """

    def __init__(self, students: List[int]):
        self.students = students

    def validate(self):
        return True

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        ids = [student.id for student in students]
        return int(set(self.students).issubset(set(ids)))

    @staticmethod
    def get_schema() -> Schema:
        return Schema({})


def equal_priority_team_sets(a: PriorityTeamSet, b: PriorityTeamSet) -> bool:
    """
    Checks if two priority team sets are equal
    """
    if len(a.priority_teams) != len(b.priority_teams):
        return False
    for priority_team_a, priority_team_b in zip(a.priority_teams, b.priority_teams):
        if priority_team_a.team_shell.id != priority_team_b.team_shell.id:
            return False
        if (
            len(
                set(priority_team_a.student_ids).symmetric_difference(
                    set(priority_team_b.student_ids)
                )
            )
            != 0
        ):
            return False
    return True


def create_new_priority_team_set(
    num_teams: int, num_students: int
) -> Tuple[PriorityTeamSet, Dict[int, Student]]:
    """
    Creates a PriorityTeamSet and a student dict
    """
    team_list: List[Team] = [Team(team_id) for team_id in range(num_teams)]
    for student_id in range(num_students):
        student: Student = Student(student_id)
        team_list[student_id % num_teams].add_student(student)
    priority_team_list: List[PriorityTeam] = [
        PriorityTeam(team, [student.id for student in team.students])
        for team in team_list
    ]
    priority_team_set: PriorityTeamSet = PriorityTeamSet(priority_team_list)
    student_dict: Dict[int, Student] = {}
    for team in team_list:
        for student in team.students:
            student_dict[student.id] = student
    return priority_team_set, student_dict


def get_priority_team(team_id: int, priority_team_set: PriorityTeamSet) -> PriorityTeam:
    """
    Gets the priority team with the given team id
    """
    if team_id < 0:
        raise ValueError(f"Team id must be positive, not {team_id}")
    if team_id >= len(priority_team_set.priority_teams):
        raise ValueError(
            f"Team id must be less than {len(priority_team_set.priority_teams)}, not {team_id}"
        )
    if priority_team_set.priority_teams[team_id].team_shell.id == team_id:
        return priority_team_set.priority_teams[team_id]
    for priority_team in priority_team_set.priority_teams:
        if priority_team.team_shell.id == team_id:
            return priority_team
    raise ValueError(f"Team {team_id} not found")


class TestMutateRobinhood(unittest.TestCase):
    def test_mutate_robinhood__only_changes_zero_or_two_team_sets(self):
        """
        Either no teams should change or two teams should change.
        """
        mutate_robinhood = RobinhoodMutation()
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        for mutation in [mutate_robinhood, mutate_robinhood_holistic]:
            priority_team_set, student_dict = create_new_priority_team_set(3, 9)
            priorities = [StudentListPriority([1, 2])]

            mutated_team_set = mutation.mutate_one(
                priority_team_set, priorities, student_dict
            )

            # Count the number of teams that changed
            changed_teams = 0
            for i in range(3):
                if (
                    get_priority_team(i, priority_team_set).student_ids
                    != get_priority_team(i, mutated_team_set).student_ids
                ):
                    changed_teams += 1

            self.assertIn(
                changed_teams, [0, 2], "Exactly 0 or 2 teams should be changed"
            )

    def test_mutate_robinhood__does_mutate_when_not_optimal(self):
        """
        The mutated team set should be different from the original team set
        """
        mutate_robinhood = RobinhoodMutation()
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        functions = [mutate_robinhood, mutate_robinhood_holistic]
        for mutation in functions:
            priority_team_set, student_dict = create_new_priority_team_set(2, 4)
            priorities = [StudentListPriority([1, 2])]

            mutated_team_set = mutation.mutate_one(
                priority_team_set.clone(), priorities, student_dict
            )

            self.assertFalse(
                equal_priority_team_sets(priority_team_set, mutated_team_set),
                "The mutated team set should be different from the original team set",
            )

    def test_mutate_robinhood__does_not_change_locked_teams(self):
        """
        Locked teams should not change
        """

        mutate_robinhood = RobinhoodMutation()
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        for mutation in [mutate_robinhood, mutate_robinhood_holistic]:
            priority_team_set, student_dict = create_new_priority_team_set(3, 9)
            priorities = [StudentListPriority([1, 2])]
            priority_team_set.priority_teams[0].team_shell.is_locked = True

            mutated_team_set = mutation.mutate_one(
                priority_team_set, priorities, student_dict
            )

            self.assertEqual(
                get_priority_team(0, priority_team_set).student_ids,
                get_priority_team(0, mutated_team_set).student_ids,
                "Locked teams should not change",
            )

    def test_mutate_robinhood__does_not_make_team_set_worse(self):
        """
        The score of the mutated team set should be at least as good as the original team set
        """
        mutate_robinhood = RobinhoodMutation()
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        for mutation in [mutate_robinhood, mutate_robinhood_holistic]:
            priority_team_set, student_dict = create_new_priority_team_set(3, 9)
            priorities = [StudentListPriority([1, 2])]

            mutated_team_set = mutation.mutate_one(
                priority_team_set, priorities, student_dict
            )

            # Reset the scores to force them to be recalculated
            priority_team_set.score = None
            mutated_team_set.score = None

            self.assertGreaterEqual(
                mutated_team_set.calculate_score(priorities, student_dict),
                priority_team_set.calculate_score(priorities, student_dict),
                "The score of the mutated team set should be at least as good as the original team set",
            )

            # Also try this when the original team set is optimal
            priority_team_set, student_dict = create_new_priority_team_set(3, 9)
            priority_team_set.priority_teams[0].student_ids = [0, 1, 2]
            priority_team_set.priority_teams[1].student_ids = [3, 4, 5]
            priority_team_set.priority_teams[2].student_ids = [6, 7, 8]

            mutated_team_set = mutation.mutate_one(
                priority_team_set, priorities, student_dict
            )

            # Reset the scores to force them to be recalculated
            priority_team_set.score = None
            mutated_team_set.score = None

            self.assertGreaterEqual(
                mutated_team_set.calculate_score(priorities, student_dict),
                priority_team_set.calculate_score(priorities, student_dict),
                "The score of the mutated team set should be at least as good as the original team set",
            )

    def test_mutate_robinhood__all_students_in_mutated_team_set(self):
        """
        All students in the original team set should be in the mutated team set
        """
        mutate_robinhood = RobinhoodMutation()
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        for mutation in [mutate_robinhood, mutate_robinhood_holistic]:
            priority_team_set, student_dict = create_new_priority_team_set(3, 9)
            priorities = [StudentListPriority([1, 2])]

            mutated_team_set = mutation.mutate_one(
                priority_team_set, priorities, student_dict
            )

            # Count the number of students in the original team set that are not in the mutated team set
            all_students = [
                student_id
                for priority_team in mutated_team_set.priority_teams
                for student_id in priority_team.student_ids
            ]

            self.assertEqual(
                len(all_students),
                9,
                "There should be the same number of students in the mutated team set as in the original team set",
            )

            missing_students = 0
            for i in range(9):
                if i not in all_students:
                    missing_students += 1

            self.assertEqual(
                missing_students, 0, "Not all students are in the mutated team set"
            )

    def test_mutate_robinhood__returns_PriorityTeamSet_object(self):
        """
        mutate_robinhood should return a PriorityTeamSet object
        """
        mutate_robinhood = RobinhoodMutation()
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        for mutation in [mutate_robinhood, mutate_robinhood_holistic]:
            priority_team_set, student_dict = create_new_priority_team_set(3, 9)
            priorities = [StudentListPriority([1, 2])]

            mutated_team_set = mutation.mutate_one(
                priority_team_set, priorities, student_dict
            )

            self.assertIsInstance(
                mutated_team_set,
                PriorityTeamSet,
                "mutate_robinhood should return a PriorityTeamSet object",
            )

    def test_mutate_robinhood_holistic__changes_only_min_and_max_scoring_teams(self):
        priority_team_set, student_dict = create_new_priority_team_set(3, 9)
        # This list of priorities make it so that the teams start with an identifiable order to their scores and can be improved when running mutate_robinhood_holistic
        priorities = [
            StudentListPriority([1, 7]),
            StudentListPriority([0]),
            StudentListPriority([4, 8]),
        ]

        # Find the min and max scoring teams
        team_scores: List[Tuple[PriorityTeam, int]] = []
        for team in priority_team_set.priority_teams:
            team_scores.append((team, utils.score(team, priorities, student_dict)))

        min_scoring_team: int = min(team_scores, key=lambda x: x[1])[0].team_shell.id
        max_scoring_team: int = max(team_scores, key=lambda x: x[1])[0].team_shell.id
        other_team: int = (
            {0, 1, 2}.difference({min_scoring_team, max_scoring_team}).pop()
        )
        mutate_robinhood_holistic = RobinhoodHolisticMutation()
        mutated_team_set = mutate_robinhood_holistic.mutate_one(
            priority_team_set.clone(), priorities, student_dict
        )

        # check that the min and max scoring teams have changed
        self.assertNotEqual(
            get_priority_team(min_scoring_team, priority_team_set).student_ids,
            get_priority_team(min_scoring_team, mutated_team_set).student_ids,
            "The min scoring team should change",
        )
        self.assertNotEqual(
            get_priority_team(max_scoring_team, priority_team_set).student_ids,
            get_priority_team(max_scoring_team, mutated_team_set).student_ids,
            "The max scoring team should change",
        )

        # Check that the other team has not changed
        self.assertEqual(
            get_priority_team(other_team, priority_team_set).student_ids,
            get_priority_team(other_team, mutated_team_set).student_ids,
            "The other team should not change",
        )
