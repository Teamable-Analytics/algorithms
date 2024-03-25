import unittest

from api.dataclasses.project import Project
from api.dataclasses.student import Student
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProviderSettings,
    MockInitialTeamsProvider,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)
from utils.validation import (
    is_unique,
    is_non_negative_integer,
    assert_can_exist_together,
)


class TestValidationHelpers(unittest.TestCase):
    def test_is_unique__works_with_primitives(self):
        self.assertTrue(is_unique([1, 2, 3]))
        self.assertFalse(is_unique([1, 2, 2]))
        self.assertTrue(is_unique(["A", "B"]))
        self.assertFalse(is_unique(["A", "A"]))

        with self.assertRaises(ValueError):
            is_unique([1, 2, "string"])

    def test_is_unique__works_with_dictionaries(self):
        self.assertTrue(is_unique([{"id": 1}, {"id": 2}, {"id": 3}], attr="id"))
        self.assertFalse(is_unique([{"id": 1}, {"id": 1}, {"id": 1}], attr="id"))

    def test_is_unique__works_with_classes(self):
        self.assertTrue(is_unique([Student(_id=1), Student(_id=2)], attr="id"))
        self.assertFalse(is_unique([Student(_id=1), Student(_id=1)], attr="id"))

    def test_is_non_negative_integer(self):
        self.assertTrue(is_non_negative_integer(0))
        self.assertTrue(is_non_negative_integer(22222))
        self.assertFalse(is_non_negative_integer(-1))
        self.assertFalse(is_non_negative_integer(-222222))

    def test_assert_can_exist_together__success(self):
        projects = [
            Project(_id=1),
            Project(_id=2),
        ]
        assert_can_exist_together(
            MockStudentProvider(MockStudentProviderSettings(number_of_students=10)),
            None,
        )
        assert_can_exist_together(
            MockStudentProvider(MockStudentProviderSettings(number_of_students=10)),
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(projects=projects)
            ),
        )
        assert_can_exist_together(
            MockStudentProvider(
                MockStudentProviderSettings(
                    number_of_students=10, project_preference_options=[1, 2]
                )
            ),
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(projects=projects)
            ),
        )
        assert_can_exist_together(
            MockStudentProvider(
                MockStudentProviderSettings(
                    number_of_students=10,
                    project_preference_options=[1, 2],
                    num_project_preferences_per_student=2,
                )
            ),
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(projects=projects)
            ),
        )

    def test_assert_can_exist_together__failure(self):
        projects = [
            Project(_id=1),
            Project(_id=2),
        ]
        with self.assertRaises(ValueError):
            assert_can_exist_together(
                MockStudentProvider(
                    MockStudentProviderSettings(
                        number_of_students=10, project_preference_options=[1, 3]
                    )
                ),
                MockInitialTeamsProvider(
                    MockInitialTeamsProviderSettings(projects=projects)
                ),
            )

        with self.assertRaises(ValueError):
            assert_can_exist_together(
                MockStudentProvider(
                    MockStudentProviderSettings(
                        number_of_students=10,
                        project_preference_options=[1, 2],
                        num_project_preferences_per_student=3,
                    )
                ),
                MockInitialTeamsProvider(
                    MockInitialTeamsProviderSettings(projects=projects)
                ),
            )

        with self.assertRaises(ValueError):
            assert_can_exist_together(
                MockStudentProvider(
                    MockStudentProviderSettings(
                        number_of_students=10, project_preference_options=[1, 2]
                    )
                ),
                None,
            )
