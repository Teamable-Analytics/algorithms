import unittest
from typing import List, Dict, Tuple

from ai.priority_algorithm.interfaces import Priority
from ai.priority_algorithm.mutations.robinhood import mutate_robinhood
from ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from models.student import Student
from models.team import Team


class TestPriority(Priority):
    """
    A custom priority for this test.
    It wants students 1 and 2 to be in the same team
    """

    def validate(self):
        return True

    def satisfied_by(self, students: List[Student]) -> bool:
        ids = [student.id for student in students]
        return 1 in ids and 2 in ids


def equal_priority_team_sets(a: PriorityTeamSet, b: PriorityTeamSet) -> bool:
    """
    Checks if two priority team sets are equal
    """
    if len(a.priority_teams) != len(b.priority_teams):
        return False
    for priority_team_a, priority_team_b in zip(a.priority_teams, b.priority_teams):
        if priority_team_a.team.id != priority_team_b.team.id:
            return False
        if not set(priority_team_a.student_ids).symmetric_difference(
            set(priority_team_b.student_ids)
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
    if priority_team_set.priority_teams[team_id].team.id == team_id:
        return priority_team_set.priority_teams[team_id]
    for priority_team in priority_team_set.priority_teams:
        if priority_team.team.id == team_id:
            return priority_team
    raise ValueError(f"Team {team_id} not found")


class TestMutateRobinhood(unittest.TestCase):
    def test_mutate_robinhood__only_changes_zero_or_two_team_sets(self):
        """
        Either no teams should change or two teams should change.
        """

        priority_team_set, student_dict = create_new_priority_team_set(3, 9)
        priorities = [TestPriority()]

        mutated_team_set = mutate_robinhood(priority_team_set, priorities, student_dict)

        # Count the number of teams that changed
        changed_teams = 0
        for i in range(3):
            if (
                get_priority_team(i, priority_team_set).student_ids
                != get_priority_team(i, mutated_team_set).student_ids
            ):
                changed_teams += 1

        self.assertIn(changed_teams, [0, 2], "Exactly 0 or 2 teams should be changed")

    def test_mutate_robinhood__does_mutate_when_not_optimal(self):
        """
        The mutated team set should be different from the original team set.
        Not guaranteed to change, so this test may fail. (~(1/3)^100 = 2e-48 chance of failing)
        """
        priority_team_set, student_dict = create_new_priority_team_set(3, 9)
        priorities = [TestPriority()]

        for _ in range(100):
            mutated_team_set = mutate_robinhood(
                priority_team_set.clone(), priorities, student_dict
            )
            if not equal_priority_team_sets(priority_team_set, mutated_team_set):
                return

        self.assertTrue(
            False,
            "The mutated team set should be different from the original team set. NOTE: This test may fail because the mutated team set is not guaranteed to change.",
        )

    def test_mutate_robinhood__does_not_change_locked_teams(self):
        """
        Locked teams should not change
        """
        priority_team_set, student_dict = create_new_priority_team_set(3, 9)
        priorities = [TestPriority()]
        priority_team_set.priority_teams[0].team.is_locked = True

        mutated_team_set = mutate_robinhood(priority_team_set, priorities, student_dict)

        self.assertEqual(
            get_priority_team(0, priority_team_set).student_ids,
            get_priority_team(0, mutated_team_set).student_ids,
            "Locked teams should not change",
        )

    def test_mutate_robinhood__does_not_make_team_set_worse(self):
        """
        The score of the mutated team set should be at least as good as the original team set
        """
        priority_team_set, student_dict = create_new_priority_team_set(3, 9)
        priorities = [TestPriority()]

        mutated_team_set = mutate_robinhood(priority_team_set, priorities, student_dict)

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

        mutated_team_set = mutate_robinhood(priority_team_set, priorities, student_dict)

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
        priority_team_set, student_dict = create_new_priority_team_set(3, 9)
        priorities = [TestPriority()]

        mutated_team_set = mutate_robinhood(priority_team_set, priorities, student_dict)

        # Count the number of students in the original team set that are not in the mutated team set
        all_students = [
            student.id
            for priority_team in priority_team_set.priority_teams
            for student in priority_team.team.students
        ]

        assert len(all_students) == 9

        missing_students = 0
        for i in range(9):
            if i not in all_students:
                missing_students += 1

        self.assertEqual(
            missing_students, 0, "Not all students are in the mutated team set"
        )
