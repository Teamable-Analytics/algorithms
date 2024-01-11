from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig, WeightAlgorithmConfig
from api.models.enums import ScenarioAttribute, RequirementOperator, Gpa, AlgorithmType
from api.models.project import Project, ProjectRequirement
from benchmarking.data.simulated_data.mock_initial_teams_provider import MockInitialTeamsProvider, \
    MockInitialTeamsProviderSettings
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings, MockStudentProvider
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.satisfy_project_requirements import SatisfyProjectRequirements
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SmallClassSize(Run):
    CLASS_SIZE = 12
    NUMBER_OF_TEAMS = 3
    NUMBER_OF_STUDENTS_PER_TEAM = 4
    NUMBER_OF_PROJECTS = 3
    CACHE_KEY = "priority_algorithm/harder_scenario/small_class_size/small_class_size/"

    def run(self, num_trials: int = 30):
        scenario = SatisfyProjectRequirements()

        projects = [
            Project(
                _id=0,
                name="Project 1",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.A.value,
                    ),
                ],
            ),
            Project(
                _id=1,
                name="Project 2",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.B.value,
                    ),
                ],
            ),
            Project(
                _id=2,
                name="Project 3",
                requirements=[
                    ProjectRequirement(
                        attribute=ScenarioAttribute.GPA.value,
                        operator=RequirementOperator.EXACTLY,
                        value=Gpa.C.value,
                    )
                ],
            )
        ]

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=self.CLASS_SIZE,
            attribute_ranges={
                ScenarioAttribute.GPA.value: [
                    (Gpa.A, 0.08333333333333333),   # 1/12 (1 person)
                    (Gpa.C, 0.08333333333333333),   # 1/12 (1 person)
                    (Gpa.D, 0.83333333333333333),   # 10/12 (9 people)
                ]
            },
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
        }

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                scenario=scenario,
                student_provider=MockStudentProvider(student_provider_settings),
                cache_key=self.CACHE_KEY,
                initial_teams_provider=MockInitialTeamsProvider(
                    settings=MockInitialTeamsProviderSettings(
                        projects=projects,
                    )
                ),
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [PriorityAlgorithmConfig()],
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
            },
        ).run(num_runs=num_trials)

        for name, simulation_artifact in artifact.items():
            for metric_name, metric in metrics.items():
                insight_set = Insight.get_output_set(
                    artifact={name: simulation_artifact},
                    metrics=[metric],
                )

                # Returns a dict[algorithm, value]
                value_dict = Insight.average_metric(
                    insight_output_set=insight_set, metric_name=metric_name
                )

                # Runtime
                runtime_dict = Insight.average_metric(
                    insight_output_set=insight_set, metric_name=Insight.KEY_RUNTIMES
                )

                print(f"{name} {metric_name}: {value_dict[name]}")
                print(f"{name} runtime: {runtime_dict[name]}")


if __name__ == "__main__":
    SmallClassSize().run()