import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import ScenarioAttribute, AlgorithmType
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings
from benchmarking.evaluations.metrics.average_timeslot_coverage import AverageTimeslotCoverage
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.evaluations.scenarios.concentrate_timeslot_and_diversify_gender_min_2_female import \
    ConcentrateTimeslotAndDiversifyGenderMin2Female
from benchmarking.runs.priority_algorithm.timeslot_and_diversify_gender_min_2.custom_student_provider import \
    CustomTwelveHundredStudentProvider
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings


class TimeSlotAndDiversifyGenderMin2(Run):
    MAX_KEEP = 50
    MAX_SPREAD = 50
    MAX_ITERATE = 500
    MAX_TIME = 1000000
    CLASS_SIZE = 120

    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        scenario = ConcentrateTimeslotAndDiversifyGenderMin2Female()

        student_provider = CustomTwelveHundredStudentProvider()

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            # "AverageTimeslotCoverage": AverageTimeslotCoverage(),
        }
        print(student_provider.get())

        # artifact: SimulationSetArtifact = SimulationSet(
        #     settings=SimulationSettings(
        #         num_teams=self.CLASS_SIZE // 4,
        #         student_provider=student_provider,
        #         scenario=scenario,
        #         cache_key="priority_algorithm/concentrate_timeslot_and_diversify_gender_min_2_female",
        #     ),
        #     algorithm_set={
        #         AlgorithmType.PRIORITY: [
        #             PriorityAlgorithmConfig(
        #                 MAX_TIME=self.MAX_TIME,
        #                 MAX_KEEP=self.MAX_KEEP,
        #                 MAX_SPREAD=self.MAX_SPREAD,
        #                 MAX_ITERATE=self.MAX_ITERATE,
        #                 name="PriorityAlgorithm",
        #             ),
        #         ],
        #     },
        # ).run(num_runs=num_trials)


if __name__ == '__main__':
    typer.run(
        TimeSlotAndDiversifyGenderMin2().start
    )
