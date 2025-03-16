import unittest
from typing import List

from algorithms.dataclasses.enums import AlgorithmType
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team import Team
from algorithms.dataclasses.team_set import TeamSet
from benchmarking.simulation.basic_simulation_set import BasicSimulationSetArtifact
from benchmarking.simulation.insight import Insight
from tests.test_benchmarking.test_simulation._data import TestMetric


class TestInsight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.team_sets: List[TeamSet] = [
            TeamSet(
                _id=1,
                teams=[
                    Team(_id=1, students=[Student(_id=1)]),
                    Team(_id=2, students=[Student(_id=2)]),
                ],
            ),
            TeamSet(
                _id=2,
                teams=[
                    Team(_id=3, students=[Student(_id=3)]),
                    Team(_id=4, students=[Student(_id=4)]),
                ],
            ),
        ]
        cls.metrics = [TestMetric(name="A"), TestMetric(name="B")]

    def test_generate__returns_correct_type_and_schema(self):
        insight_output = Insight(
            team_sets=self.team_sets,
            metrics=self.metrics,
            run_times=[1, 1],
        ).generate()

        self.assertEqual(len(insight_output.keys()), 3)
        for key in insight_output.keys():
            self.assertEqual(len(insight_output[key]), len(self.team_sets))
        self.assertTrue(Insight.KEY_RUNTIMES in insight_output)

        insight_output_2 = Insight(
            team_sets=self.team_sets,
            metrics=self.metrics,
        ).generate()

        self.assertEqual(len(insight_output_2.keys()), 3)
        for key in insight_output_2.keys():
            if key == Insight.KEY_RUNTIMES:
                self.assertIsNone(insight_output_2[key])
                continue
            self.assertEqual(len(insight_output_2[key]), len(self.team_sets))

    def test_average_metric__works_with_get_output_set(self):
        mock_basic_simulation_set: BasicSimulationSetArtifact = {
            AlgorithmType.RANDOM: (self.team_sets, [1, 1]),
            AlgorithmType.WEIGHT: (self.team_sets, [1, 1]),
        }

        insight_output_set = Insight.get_output_set(
            mock_basic_simulation_set, metrics=self.metrics
        )
        average_metric_insight = Insight.average_metric(
            insight_output_set, metric_name="A"
        )

        self.assertEqual(len(average_metric_insight.keys()), 2)
        for key in average_metric_insight.keys():
            # can be an int if the numbers divide perfectly
            self.assertIsInstance(average_metric_insight[key], (int, float))

    def test_metric_stdev__works_with_get_output_set(self):
        mock_basic_simulation_set: BasicSimulationSetArtifact = {
            AlgorithmType.RANDOM: (self.team_sets, [1, 1]),
            AlgorithmType.WEIGHT: (self.team_sets, [1, 1]),
        }

        insight_output_set = Insight.get_output_set(
            mock_basic_simulation_set, metrics=self.metrics
        )
        metric_stdev_insight = Insight.metric_stdev(insight_output_set, metric_name="A")

        self.assertEqual(len(metric_stdev_insight.keys()), 2)
        for key in metric_stdev_insight.keys():
            # can be an int if the numbers divide perfectly
            self.assertIsInstance(metric_stdev_insight[key], (int, float))
