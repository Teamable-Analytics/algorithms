import unittest

from api.dataclasses.enums import ScenarioAttribute, Race, Gender
from api.dataclasses.student import Student
from api.dataclasses.team import Team
from api.dataclasses.team_set import TeamSet
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus


class TestAverageSoloStatus(unittest.TestCase):
    def setUp(self):
        self.class_with_minority_students = TeamSet(
            _id="1",
            teams=[
                Team(
                    _id=1,
                    students=[
                        Student(
                            _id=1,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                        Student(
                            _id=2,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                        Student(
                            _id=3,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                    ],
                )
            ],
        )

        self.class_with_only_1_minority_student = TeamSet(
            _id="1",
            teams=[
                Team(
                    _id=1,
                    students=[
                        Student(
                            _id=1,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.European.value],
                            },
                        ),
                        Student(
                            _id=2,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=2,
                    students=[
                        Student(
                            _id=3,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                        Student(
                            _id=4,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                    ],
                ),
            ],
        )

        self.class_with_all_minority_students = TeamSet(
            _id="1",
            teams=[
                Team(
                    _id=1,
                    students=[
                        Student(
                            _id=1,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.European.value],
                            },
                        ),
                        Student(
                            _id=2,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=2,
                    students=[
                        Student(
                            _id=3,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.East_Asian.value],
                            },
                        ),
                        Student(
                            _id=4,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.European.value],
                            },
                        ),
                    ],
                ),
            ],
        )

        self.class_with_all_minority_students_different_attribute = TeamSet(
            _id="1",
            teams=[
                Team(
                    _id=1,
                    students=[
                        Student(
                            _id=1,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.European.value],
                                ScenarioAttribute.GENDER.value: [Gender.OTHER.value],
                            },
                        ),
                        Student(
                            _id=2,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                                ScenarioAttribute.GENDER.value: [Gender.OTHER.value],
                            },
                        ),
                    ],
                ),
                Team(
                    _id=2,
                    students=[
                        Student(
                            _id=3,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                                ScenarioAttribute.GENDER.value: [Gender.OTHER.value],
                            },
                        ),
                        Student(
                            _id=4,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                                ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                            },
                        ),
                    ],
                ),
            ],
        )

        self.class_with_one_student_with_double_minority = TeamSet(
            _id="1",
            teams=[
                Team(
                    _id=1,
                    students=[
                        Student(
                            _id=idx,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.Other.value],
                                ScenarioAttribute.GENDER.value: [Gender.OTHER.value],
                            },
                        )
                        for idx in range(1, 10)
                    ]
                    + [
                        Student(
                            _id=0,
                            attributes={
                                ScenarioAttribute.RACE.value: [Race.European.value],
                                ScenarioAttribute.GENDER.value: [Gender.MALE.value],
                            },
                        )
                    ],
                )
            ],
        )

    def test_calculate__should_return_0_when_the_minority_group_not_exist_in_class(
        self,
    ):
        metric = AverageSoloStatus(
            minority_groups_map={
                ScenarioAttribute.RACE.value: [
                    race.value for race in Race if race != Race.Other
                ]
            }
        )

        actual = metric.calculate(self.class_with_minority_students)

        self.assertEqual(actual, 0)

    def test_calculate__should_return_0_25_when_one_out_of_4_is_solo_status(
        self,
    ):
        metric = AverageSoloStatus(
            minority_groups_map={ScenarioAttribute.RACE.value: [Race.European.value]}
        )

        actual = metric.calculate(self.class_with_only_1_minority_student)

        self.assertEqual(actual, 0.25)

    def test_calculate__should_return_1_when_everyone_is_solo_status(
        self,
    ):
        metric = AverageSoloStatus(
            minority_groups_map={
                ScenarioAttribute.RACE.value: [race.value for race in Race]
            }
        )

        actual = metric.calculate(self.class_with_all_minority_students)

        self.assertEqual(actual, 1)

    def test_calculate__should_return_0_5_when_2_out_of_4_students_are_in_solo_status(
        self,
    ):
        metric = AverageSoloStatus(
            minority_groups_map={
                ScenarioAttribute.RACE.value: [Race.European.value],
                ScenarioAttribute.GENDER.value: [Gender.MALE.value],
            }
        )

        actual = metric.calculate(
            self.class_with_all_minority_students_different_attribute
        )

        self.assertAlmostEqual(actual, 0.5)

        # Sanity check: ensure that the metric is not affected by the order of the teams
        metric_sanity = AverageSoloStatus(
            minority_groups_map={
                ScenarioAttribute.RACE.value: [Race.European.value],
            }
        )

        actual_sanity = metric_sanity.calculate(
            self.class_with_all_minority_students_different_attribute
        )

        self.assertAlmostEqual(actual_sanity, 0.25)

    def test_calculate__should_return_one_tenth_even_if_they_are_inter_homogeneity_aka_no_double_counting(
        self,
    ):
        metric = AverageSoloStatus(
            minority_groups_map={
                ScenarioAttribute.RACE.value: [Race.European.value],
                ScenarioAttribute.GENDER.value: [Gender.MALE.value],
            }
        )

        actual = metric.calculate(self.class_with_one_student_with_double_minority)

        self.assertAlmostEqual(actual, 0.1)
