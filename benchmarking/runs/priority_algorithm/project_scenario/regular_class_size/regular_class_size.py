import itertools
import random

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig, WeightAlgorithmConfig
from api.models.enums import ScenarioAttribute, RequirementOperator, Gpa, AlgorithmType, Gender, Race
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


class RegularClassSize(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 24
    NUMBER_OF_STUDENTS_PER_TEAM = 5
    NUMBER_OF_PROJECTS = 3
    CACHE_KEY = "priority_algorithm/project_scenario/regular_class_size/regular_class_size/"

    def run(self, num_trials: int = 100):
        scenario = SatisfyProjectRequirements()

        all_projects = [
            Project(
                _id=-1,
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
                _id=-2,
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
                _id=-3,
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

        random.shuffle(all_projects)
        projects = []
        for idx, proj in enumerate(itertools.cycle(all_projects)):
            projects.append(Project(
                _id=idx,
                name=f'{proj.name} - {idx}',
                requirements=proj.requirements,
            ))

            if len(projects) == self.NUMBER_OF_TEAMS:
                break


        initial_teams_provider = MockInitialTeamsProvider(
            settings=MockInitialTeamsProviderSettings(
                projects=projects,
            )
        )

        student_provider_settings = MockStudentProviderSettings(
            number_of_students=self.CLASS_SIZE,
            attribute_ranges={
                ScenarioAttribute.GPA.value: [
                    (Gpa.A, 0.06666666666666667),
                    (Gpa.B, 0.06666666666666667),
                    (Gpa.C, 0.06666666666666667),
                    (Gpa.D, 0.8),
                ],
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 0.7),
                    (Gender.FEMALE, 0.3),
                ],
                ScenarioAttribute.RACE.value: [
                    (Race.African, 0.1),
                    (Race.European, 0.1),
                    (Race.East_Asian, 0.1),
                    (Race.South_Asian, 0.1),
                    (Race.South_East_Asian, 0.1),
                    (Race.First_Nations_or_Indigenous, 0.1),
                    (Race.Hispanic_or_Latin_American, 0.1),
                    (Race.Middle_Eastern, 0.1),
                    (Race.Other, 0.2),
                ],
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
                initial_teams_provider=initial_teams_provider,
            ),
            algorithm_set={
                AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(),
                ],
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
    RegularClassSize().run()