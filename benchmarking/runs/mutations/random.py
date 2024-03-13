from api.dataclasses.enums import ScenarioAttribute, Gender, Race
from benchmarking.data.simulated_data.realistic_class.providers import get_realistic_projects, \
    RealisticMockInitialTeamsProvider, RealisticMockStudentProvider
from benchmarking.evaluations.metrics.average_project_requirements_coverage import AverageProjectRequirementsCoverage
from benchmarking.evaluations.metrics.average_solo_status import AverageSoloStatus
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.satisfy_project_requirements_and_diversify_female_min_of_2_and_diversify_african_min_of_2 import \
    SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class RandomMutationBenchmark(Run):
    def start(self, num_trials: int = 10, generate_graphs: bool = True):
        class_sizes = [50, 100, 250, 500]

        scenario = SatisfyProjectRequirementsAndDiversifyFemaleMinOf2AndDiversifyAfricanMinOf2()

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            "AverageCosineDifferenceGender": AverageCosineDifference(
                attribute_filter=[
                    ScenarioAttribute.GENDER.value
                ]
            ),
            "AverageCosineDifferenceRace": AverageCosineDifference(
                attribute_filter=[
                    ScenarioAttribute.RACE.value
                ]
            ),
            "AverageSoloStatus": AverageSoloStatus(
                minority_groups={
                    ScenarioAttribute.GENDER.value: [_.value for _ in Gender.values()],
                    ScenarioAttribute.MAJOR.value: [_.value for _ in Race.values()],
                }
            ),
        }

        initial_teams_provider = RealisticMockInitialTeamsProvider()

        for class_size in class_sizes:
            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=RealisticMockStudentProvider(),
                    cache_key=f"priority_algorithm/internal_parameter_exploration/class_size_120/combined_run/",
                    initial_teams_provider=initial_teams_provider,
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                            MAX_ITERATE=max_iterations,
                            MAX_TIME=1_000_000,
                            START_TYPE=start_type,
                            name=f"max_keep_{max_keep}-max_spread_{max_spread}-max_iterations_{max_iterations}-{start_type.value}_start",
                        )
                        for max_keep in max_keep_range
                        for max_spread in max_spread_range
                        for max_iterations in max_iterations_range
                    ]
                },
            ).run(num_runs=num_trials)
