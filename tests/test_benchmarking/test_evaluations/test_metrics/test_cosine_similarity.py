import unittest

from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from benchmarking.evaluations.metrics.cosine_similarity import (
    AverageCosineSimilarity,
    AverageCosineDifference,
)


class TestCosineSimilarity(unittest.TestCase):
    def setUp(self):
        self.mock_students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=12,
                attribute_ranges={
                    1: [
                        (1, 0.5),
                        (2, 0.5),
                    ]
                },
            )
        ).get()

        self.team_set_same_attribute = TeamSet(teams=[Team(_id=1), Team(_id=2)])
        for student in self.mock_students:
            if student.attributes[1] == [1]:
                self.team_set_same_attribute.teams[0].students.append(student)
            else:
                self.team_set_same_attribute.teams[1].students.append(student)

        self.team_set_distributed_attribute = TeamSet(teams=[Team(_id=1), Team(_id=2)])
        for i, student in enumerate(
            sorted(self.mock_students, key=lambda x: x.attributes[1][0])
        ):
            if i % 2 == 0:
                self.team_set_distributed_attribute.teams[0].students.append(student)
            else:
                self.team_set_distributed_attribute.teams[1].students.append(student)

    def test_calculate__metric_between_zero_and_one(self):
        score = AverageCosineSimilarity().calculate(self.team_set_same_attribute)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

        score = AverageCosineSimilarity().calculate(self.team_set_distributed_attribute)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_calculate__calculates_expected_metric(self):
        self.assertEqual(
            1, AverageCosineSimilarity().calculate(self.team_set_same_attribute)
        )
        self.assertEqual(
            0.4,
            AverageCosineSimilarity().calculate(self.team_set_distributed_attribute),
        )


class TestCosineDifference(unittest.TestCase):
    def setUp(self):
        self.mock_students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=12,
                attribute_ranges={
                    1: [
                        (1, 0.5),
                        (2, 0.5),
                    ]
                },
            )
        ).get()

        self.team_set_same_attribute = TeamSet(teams=[Team(_id=1), Team(_id=2)])
        for student in self.mock_students:
            if student.attributes[1] == [1]:
                self.team_set_same_attribute.teams[0].students.append(student)
            else:
                self.team_set_same_attribute.teams[1].students.append(student)

        self.team_set_distributed_attribute = TeamSet(teams=[Team(_id=1), Team(_id=2)])
        for i, student in enumerate(
            sorted(self.mock_students, key=lambda x: x.attributes[1][0])
        ):
            if i % 2 == 0:
                self.team_set_distributed_attribute.teams[0].students.append(student)
            else:
                self.team_set_distributed_attribute.teams[1].students.append(student)

    def test_calculate__metric_between_zero_and_one(self):
        score = AverageCosineDifference().calculate(self.team_set_same_attribute)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

        score = AverageCosineDifference().calculate(self.team_set_distributed_attribute)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_calculate__calculates_expected_metric(self):
        self.assertEqual(
            0, AverageCosineDifference().calculate(self.team_set_same_attribute)
        )
        self.assertEqual(
            0.6,
            AverageCosineDifference().calculate(self.team_set_distributed_attribute),
        )