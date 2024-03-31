import unittest
from typing import List

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations.local_max import LocalMaxMutation
from api.ai.priority_algorithm.mutations.local_max_double_random import (
    LocalMaxDoubleRandomMutation,
)
from api.ai.priority_algorithm.mutations.local_max_random import LocalMaxRandomMutation
from api.ai.priority_algorithm.priority.interfaces import Priority
from benchmarking.simulation.mock_algorithm import MockAlgorithm
from tests.test_api.test_ai.test_priority_algorithm.test_mutations._data import (
    EvenPriority,
    JohnPriority,
    get_mock_team_set,
    get_mock_student_dict,
    get_mock_students,
)


class TestMutations(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.priorities: List[Priority] = [EvenPriority()]
        cls.priority_team_set = get_mock_team_set(get_mock_students())
        cls.students = get_mock_students()
        cls.student_dict = get_mock_student_dict(get_mock_students())
        cls.local_max_mutation = LocalMaxMutation()
        cls.local_max_random_mutation = LocalMaxRandomMutation()
        cls.local_max_double_random_mutation = LocalMaxDoubleRandomMutation()

    def test_local_max__returns_priority_teams(self):
        priority_team_set = self.local_max_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_local_max__improves_team_based_on_priority(self):
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = self.local_max_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)

    def test_local_max__improves_team_with_two_priorities(self):
        self.priorities.append(JohnPriority())
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = self.local_max_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        priority_team_set.score = None
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)

    def test_mutate_local_max_random__returns_priority_teams(self):
        priority_team_set = self.local_max_random_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_mutate_local_max_random__improves_score(self):
        self.priorities.append(JohnPriority())
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = self.local_max_random_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        priority_team_set.score = None
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)

    def test_mutate_local_max_double_random__returns_priority_teams(self):
        priority_team_set = self.local_max_double_random_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        self.assertIsInstance(priority_team_set, PriorityTeamSet)
        for team in priority_team_set.priority_teams:
            self.assertIsInstance(team, PriorityTeam)

    def test_mutate_local_max_double_double_random__improves_score(self):
        self.priorities.append(JohnPriority())
        score_before = self.priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        priority_team_set = self.local_max_double_random_mutation.mutate_one(
            self.priority_team_set,
            self.priorities,
            self.student_dict,
            MockAlgorithm.get_team_generation_options(
                num_students=10, num_teams=2, min_team_size=1, max_team_size=10
            ),
        )
        priority_team_set.score = None
        score_after = priority_team_set.calculate_score(
            self.priorities, self.student_dict
        )
        self.assertGreater(score_after, score_before)
