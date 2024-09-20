import unittest

from api.dataclasses.enums import RequirementOperator, RequirementsCriteria
from api.dataclasses.project import ProjectRequirement
from api.dataclasses.project.dataclass import MIN_NON_ZERO_SATISFACTION
from api.dataclasses.student import Student


def count(start=0):
    while True:
        yield start
        start += 1


def student_meeting_requirement(requirement: ProjectRequirement) -> Student:
    correct_value = None
    if requirement.operator == RequirementOperator.EXACTLY:
        correct_value = requirement.value
    if requirement.operator == RequirementOperator.LESS_THAN:
        correct_value = requirement.value - 1
    if requirement.operator == RequirementOperator.MORE_THAN:
        correct_value = requirement.value + 1

    return Student(
        _id=next(count()), attributes={requirement.attribute: [correct_value]}
    )


def student_not_meeting_requirement(requirement: ProjectRequirement) -> Student:
    incorrect_value = None
    if requirement.operator == RequirementOperator.EXACTLY:
        incorrect_value = requirement.value - 1
    if requirement.operator == RequirementOperator.LESS_THAN:
        incorrect_value = requirement.value + 1
    if requirement.operator == RequirementOperator.MORE_THAN:
        incorrect_value = requirement.value - 1

    return Student(
        _id=next(count()), attributes={requirement.attribute: [incorrect_value]}
    )


class TestProjectRequirementDataclass(unittest.TestCase):
    def test__has_default_criteria(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=1,
        )

        self.assertTrue(bool(requirement))

    def test_validate__cannot_pass_n_members_criteria_without_passing_n(self):
        with self.assertRaises(ValueError):
            ProjectRequirement(
                attribute=1,
                operator=RequirementOperator.EXACTLY,
                value=1,
                criteria=RequirementsCriteria.N_MEMBERS,
            )

    def test_met_by_student__with_operator__exactly(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=100,
        )
        student_meeting = Student(_id=1, attributes={1: [requirement.value]})
        student_not_meeting = Student(_id=1, attributes={1: [requirement.value + 1]})

        self.assertTrue(requirement.met_by_student(student_meeting))
        self.assertFalse(requirement.met_by_student(student_not_meeting))

    def test_met_by_student__with_operator__less_than(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.LESS_THAN,
            value=100,
        )
        student_meeting_1 = Student(_id=1, attributes={1: [requirement.value - 1]})
        student_meeting_2 = Student(
            _id=1, attributes={1: [requirement.value - 1, requirement.value]}
        )
        student_not_meeting = Student(_id=1, attributes={1: [requirement.value + 1]})

        self.assertTrue(requirement.met_by_student(student_meeting_1))
        self.assertTrue(requirement.met_by_student(student_meeting_2))
        self.assertFalse(requirement.met_by_student(student_not_meeting))

    def test_met_by_student__with_operator__more_than(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.MORE_THAN,
            value=100,
        )
        student_meeting_1 = Student(_id=1, attributes={1: [requirement.value + 1]})
        student_meeting_2 = Student(
            _id=1, attributes={1: [requirement.value + 1, requirement.value]}
        )
        student_not_meeting_1 = Student(_id=1, attributes={1: [requirement.value - 1]})
        student_not_meeting_2 = Student(_id=1, attributes={1: [requirement.value]})

        self.assertTrue(requirement.met_by_student(student_meeting_1))
        self.assertTrue(requirement.met_by_student(student_meeting_2))
        self.assertFalse(requirement.met_by_student(student_not_meeting_1))
        self.assertFalse(requirement.met_by_student(student_not_meeting_2))

    def test_satisfaction_by_students__cannot_produce_non_zero_value_below_min(self):
        for criteria in RequirementsCriteria:
            requirement = ProjectRequirement(
                attribute=1,
                operator=RequirementOperator.EXACTLY,
                value=100,
                criteria=criteria,
                num_members_required=2,
            )

            student_groups_set = [
                [
                    student_not_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                ],
                [
                    student_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                ],
                [
                    student_meeting_requirement(requirement),
                    student_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                    student_not_meeting_requirement(requirement),
                ],
            ]

            for student_group in student_groups_set:
                satisfaction = requirement.satisfaction_by_students(student_group)
                if satisfaction == 0:
                    continue
                self.assertGreaterEqual(
                    satisfaction,
                    MIN_NON_ZERO_SATISFACTION,
                    msg=f"All non-zero requirement satisfaction scores for a team should be greater than or equal to {MIN_NON_ZERO_SATISFACTION}",
                )

    def test_satisfaction_by_students__with_criteria__someone(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=100,
            criteria=RequirementsCriteria.SOMEONE,
        )

        students_1 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
        ]

        students_2 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        students_3 = [
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        self.assertEqual(
            requirement.satisfaction_by_students(students_1),
            requirement.satisfaction_by_students(students_2),
        )

        self.assertEqual(
            requirement.satisfaction_by_students(students_2),
            requirement.satisfaction_by_students(students_3),
        )

        self.assertEqual(1, requirement.satisfaction_by_students(students_1))

        students_4 = [
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        self.assertEqual(0, requirement.satisfaction_by_students(students_4))

    def test_satisfaction_by_students__with_criteria__everyone(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=100,
            criteria=RequirementsCriteria.EVERYONE,
        )

        students_1 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
        ]

        self.assertEqual(1, requirement.satisfaction_by_students(students_1))

        students_2 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        students_3 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        students_4 = [
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        students_5 = [
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        self.assertGreater(
            requirement.satisfaction_by_students(students_2),
            requirement.satisfaction_by_students(students_3),
        )

        self.assertGreater(
            requirement.satisfaction_by_students(students_3),
            requirement.satisfaction_by_students(students_4),
        )

        self.assertGreater(
            requirement.satisfaction_by_students(students_4),
            requirement.satisfaction_by_students(students_5),
        )

        self.assertEqual(0, requirement.satisfaction_by_students(students_5))

    def test_satisfaction_by_students__with_criteria__everyone__prefers_first_student(
        self,
    ):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=100,
            criteria=RequirementsCriteria.EVERYONE,
        )

        original_team_a = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]
        original_satisfaction_a = requirement.satisfaction_by_students(original_team_a)
        new_satisfaction_a = requirement.satisfaction_by_students(
            original_team_a + [student_meeting_requirement(requirement)]
        )

        original_team_b = [
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]
        original_satisfaction_b = requirement.satisfaction_by_students(original_team_b)
        new_satisfaction_b = requirement.satisfaction_by_students(
            original_team_b + [student_meeting_requirement(requirement)]
        )

        self.assertGreater(
            new_satisfaction_b - original_satisfaction_b,
            new_satisfaction_a - original_satisfaction_a,
        )

    def test_satisfaction_by_students__with_criteria__n_members(self):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=100,
            criteria=RequirementsCriteria.N_MEMBERS,
            num_members_required=2,
        )

        students_1 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
        ]

        self.assertEqual(1, requirement.satisfaction_by_students(students_1))

        students_2 = [
            student_meeting_requirement(requirement),
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        self.assertEqual(
            requirement.satisfaction_by_students(students_1),
            requirement.satisfaction_by_students(students_2),
        )

        students_3 = [
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        self.assertGreater(
            requirement.satisfaction_by_students(students_2),
            requirement.satisfaction_by_students(students_3),
        )

        students_4 = [
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]

        self.assertGreater(
            requirement.satisfaction_by_students(students_3),
            requirement.satisfaction_by_students(students_4),
        )

        self.assertEqual(0, requirement.satisfaction_by_students(students_4))

    def test_satisfaction_by_students__with_criteria__n_members__prefers_first_student(
        self,
    ):
        requirement = ProjectRequirement(
            attribute=1,
            operator=RequirementOperator.EXACTLY,
            value=100,
            criteria=RequirementsCriteria.N_MEMBERS,
            num_members_required=2,
        )

        original_team_a = [
            student_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]
        original_satisfaction_a = requirement.satisfaction_by_students(original_team_a)
        new_satisfaction_a = requirement.satisfaction_by_students(
            original_team_a + [student_meeting_requirement(requirement)]
        )

        original_team_b = [
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
            student_not_meeting_requirement(requirement),
        ]
        original_satisfaction_b = requirement.satisfaction_by_students(original_team_b)
        new_satisfaction_b = requirement.satisfaction_by_students(
            original_team_b + [student_meeting_requirement(requirement)]
        )

        self.assertGreater(
            new_satisfaction_b - original_satisfaction_b,
            new_satisfaction_a - original_satisfaction_a,
        )
