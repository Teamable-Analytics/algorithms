import unittest

from api.models.enums import ScenarioAttribute
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.metrics.average_timeslot_coverage import AverageTimeslotCoverage


class TestAverageTimeslotCoverage(unittest.TestCase):
    def setUp(self):
        self.available_timeslots = [1, 2, 3, 4, 5, 6, 7, 8]

        self.teamset_that_everyone_is_available = TeamSet(
            _id='0',
            teams=[
                Team(
                    _id=0,
                    students=[
                        Student(_id=1, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4, 5, 6, 7, 8]
                        }),
                        Student(_id=2, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4, 5, 6, 7, 8]
                        }),
                        Student(_id=3, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4, 5, 6, 7, 8]
                        }),
                    ]
                ),
                Team(
                    _id=1,
                    students=[
                        Student(_id=4, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4, 5, 6, 7, 8]
                        }),
                        Student(_id=5, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4, 5, 6, 7, 8]
                        }),
                        Student(_id=6, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3, 4, 5, 6, 7, 8]
                        }),
                    ]
                ),
            ]
        )

        self.teamset_that_everyone_is_available_on_one_timeslot = TeamSet(
            _id='1',
            teams=[
                Team(
                    _id=0,
                    students=[
                        Student(_id=1, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1]
                        }),
                        Student(_id=2, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1]
                        }),
                        Student(_id=3, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1]
                        }),
                    ]
                ),
                Team(
                    _id=1,
                    students=[
                        Student(_id=4, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [2]
                        }),
                        Student(_id=5, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [2]
                        }),
                        Student(_id=6, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [2]
                        }),
                    ]
                ),
            ]
        )

        self.teamset_that_noone_agree_on_one_timeslot = TeamSet(
            _id='2',
            teams=[
                Team(
                    _id=0,
                    students=[
                        Student(_id=1, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2]
                        }),
                        Student(_id=2, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [3, 4]
                        }),
                        Student(_id=3, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [5, 6]
                        }),
                    ]
                ),
                Team(
                    _id=1,
                    students=[
                        Student(_id=4, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [2, 3]
                        }),
                        Student(_id=5, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 4]
                        }),
                        Student(_id=6, attributes={
                            ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [7, 8]
                        }),
                    ]
                ),
            ]
        )

        self.teamset_that_everyone_is_available_but_not_mutually = TeamSet(
            _id='3',
            teams=[
                Team(
                    _id=0,
                    students=[
                        Student(
                            _id=1,
                            attributes={
                                ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [1, 2, 3],
                            }
                        ),
                        Student(
                            _id=2,
                            attributes={
                                ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [4, 5, 6],
                            },
                        ),
                        Student(
                            _id=3,
                            attributes={
                                ScenarioAttribute.TIMESLOT_AVAILABILITY.value: [5, 6, 7, 8],
                            },
                        ),
                    ],
                ),
            ],
        )

    def test_calculate__should_return_1_when_everyone_is_available(self):
        metrics = AverageTimeslotCoverage(available_timeslots=self.available_timeslots,
                                          timeslot_attribute_value=ScenarioAttribute.TIMESLOT_AVAILABILITY.value)

        actual = metrics.calculate(self.teamset_that_everyone_is_available)

        self.assertEqual(1, actual)

    def test_calculate__should_return_one_eighth_when_noone_is_available(self):
        metrics = AverageTimeslotCoverage(available_timeslots=self.available_timeslots,
                                          timeslot_attribute_value=ScenarioAttribute.TIMESLOT_AVAILABILITY.value)

        actual = metrics.calculate(self.teamset_that_everyone_is_available_on_one_timeslot)

        # 1/8 because everyone only has 1 available timeslot and there are 8 available timeslots
        self.assertEqual(1 / 8, actual)

    def test_calculate__should_return_0_noone_agrees_on_a_timeslot(self):
        metrics = AverageTimeslotCoverage(available_timeslots=self.available_timeslots,
                                          timeslot_attribute_value=ScenarioAttribute.TIMESLOT_AVAILABILITY.value)

        actual = metrics.calculate(self.teamset_that_noone_agree_on_one_timeslot)

        self.assertEqual(0, actual)

    def test_calculate__should_return_0_when_noone_is_available_mutually(self):
        metrics = AverageTimeslotCoverage(available_timeslots=self.available_timeslots,
                                          timeslot_attribute_value=ScenarioAttribute.TIMESLOT_AVAILABILITY.value)

        actual = metrics.calculate(self.teamset_that_everyone_is_available_but_not_mutually)

        self.assertEqual(0, actual)
