import unittest
from typing import List

from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.data.real_data.cosc341_w2021_t2_provider.providers import (
    COSC341W2021T2StudentProvider,
    COSC341W2021T2TeamConfigurationProvider,
)


class TestCOSC341W2021T2TeamConfigurationProvider(unittest.TestCase):
    def test_get__returns_correct_type(self):
        team_set = COSC341W2021T2TeamConfigurationProvider().get()

        self.assertIsInstance(team_set, TeamSet)

    def test_get__teams_contains_all_students_once(self):
        team_set = COSC341W2021T2TeamConfigurationProvider().get()
        teams_students = []
        for team in team_set.teams:
            teams_students.extend(team.students)

        students = COSC341W2021T2StudentProvider().get()

        self.assertEqual(len(students), len(teams_students))
        ids = [_.id for _ in students]
        teams_ids = [_.id for _ in teams_students]
        self.assertEqual(len(set(ids)), len(teams_ids))
        self.assertListEqual(sorted(ids), sorted(teams_ids))


class TestCOSC341W2021T2StudentProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = COSC341W2021T2StudentProvider()

    def test_get__returns_correct_type(self):
        students = self.provider.get()
        self.assertIsInstance(students, List)
        self.assertIsInstance(students[0], Student)

    def test_get__seed_shuffles_list(self):
        students = self.provider.get()
        students_seeded = self.provider.get(seed=5)
        students_seeded_2 = self.provider.get(seed=5)
        students_seeded_3 = self.provider.get(seed=100)

        ids = [_.id for _ in students]
        ids_seeded = [_.id for _ in students_seeded]
        ids_seeded_2 = [_.id for _ in students_seeded_2]
        ids_seeded_3 = [_.id for _ in students_seeded_3]

        # Same students
        self.assertListEqual(sorted(ids), sorted(ids_seeded))

        # But different order
        self.assertFalse(all([a == b for a, b in zip(ids, ids_seeded)]))

        # And the same seed produces the same order
        self.assertListEqual(ids_seeded, ids_seeded_2)

        # And different seed produces different order
        self.assertFalse(all([a == b for a, b in zip(ids_seeded_2, ids_seeded_3)]))

    def test_num_students__is_same_as_len_of_get(self):
        self.assertEqual(self.provider.num_students, len(self.provider.get()))

    def test_max_project_preferences_per_student__is_zero(self):
        self.assertEqual(0, self.provider.max_project_preferences_per_student)
