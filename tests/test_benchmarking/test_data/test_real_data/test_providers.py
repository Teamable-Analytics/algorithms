import unittest
from typing import List

from api.models.student import Student
from api.models.team import Team
from benchmarking.data.real_data.cosc341_w2022_provider.providers import (
    COSC341W2021T2StudentProvider,
    COSC341W2021T2InitialTeamsProvider,
)


class TestCOSC341W2021T2InitialTeamsProvider(unittest.TestCase):
    def test_get__returns_correct_type(self):
        teams = COSC341W2021T2InitialTeamsProvider().get()

        self.assertIsInstance(teams, List)
        self.assertIsInstance(teams[0], Team)

    def test_get__teams_contains_all_students_once(self):
        teams = COSC341W2021T2InitialTeamsProvider().get()
        teams_students = []
        for team in teams:
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

        ids = [_.id for _ in students]
        ids_seeded = [_.id for _ in students_seeded]

        # Same students
        self.assertListEqual(sorted(ids), sorted(ids_seeded))

        # But different order
        for a, b in zip(ids, ids_seeded):
            self.assertNotEqual(a, b)

    def test_num_students__is_same_as_len_of_get(self):
        self.assertEqual(self.provider.num_students, len(self.provider.get()))

    def test_max_project_preferences_per_student__is_zero(self):
        self.assertEqual(0, self.provider.max_project_preferences_per_student)
