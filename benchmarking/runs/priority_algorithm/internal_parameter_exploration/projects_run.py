import itertools
import random
import re
from typing import List, Dict, Tuple

import typer

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.models.enums import RequirementsCriteria, Gpa
from api.models.enums import (
    ScenarioAttribute,
    RequirementOperator,
    AlgorithmType,
)
from api.models.project import Project, ProjectRequirement
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)
from benchmarking.evaluations.goals import ProjectRequirementGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.internal_parameter_exploration.run_utils import (
    plot_and_save_points_dict,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class SatisfyProjectRequirements(Scenario):
    @property
    def name(self) -> str:
        return "Students Meet Project Requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            WeightGoal(project_requirement_weight=1),
        ]


class RegularClassSize(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30
    NUMBER_OF_STUDENTS_PER_TEAM = 4
    NUMBER_OF_PROJECTS = 3

    def start(self, num_trials: int = 30, generate_graphs: bool = True):
        # Ranges
        max_keep_range = [1] + list(range(5, 31, 5))
        max_spread_range = [1] + list(range(5, 31, 5))
        max_iterations_range = [1, 5, 10, 20, 30]

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
            ),
        ]

        random.shuffle(all_projects)
        projects = []
        for idx, proj in enumerate(itertools.cycle(all_projects)):
            projects.append(
                Project(
                    _id=idx,
                    name=f"{proj.name} - {idx}",
                    requirements=proj.requirements,
                )
            )

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
                    (Gpa.A.value, float(1 / 15)),
                    (Gpa.B.value, float(1 / 15)),
                    (Gpa.C.value, float(1 / 15)),
                    (Gpa.D.value, float(12 / 15)),
                ],
            },
        )

        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
        }

        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {start_type: {} for start_type in start_types}
        for start_type in start_types:
            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=MockStudentProvider(student_provider_settings),
                    cache_key=f"priority_algorithm/internal_parameter_exploration/class_size_120/projects_run/",
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

            for name, simulation_artifact in artifact.items():
                match = re.search(
                    r"max_keep_(\d+)-max_spread_(\d+)-max_iterations_(\d+)",
                    name,
                )
                if match:
                    max_keep = int(match.group(1))
                    max_spread = int(match.group(2))
                    max_iterations = int(match.group(3))
                    artifacts_dict[start_type][
                        (max_keep, max_spread, max_iterations)
                    ] = simulation_artifact

        if generate_graphs:
            for metric_name, metric in metrics.items():
                points_dict = {}
                for start_type, artifacts in artifacts_dict.items():
                    points: Dict[Tuple[int, int, int], float] = {}
                    for point_location, simulation_artifact in artifacts.items():
                        insight_set = Insight.get_output_set(
                            artifact={"arbitrary_name": simulation_artifact},
                            metrics=[metric],
                        )
                        # Returns a dict[algorithm, value]
                        value_dict = Insight.average_metric(
                            insight_output_set=insight_set, metric_name=metric_name
                        )
                        # Get first value, assumes only one algorithm being run
                        value = list(value_dict.values())[0]
                        points[point_location] = value
                    points_dict[start_type] = points

                plot_and_save_points_dict(
                    points_dict,
                    max_iterations_range,
                    metric,
                    "3 Project Scenario",
                    "projects",
                )


if __name__ == "__main__":
    typer.run(RegularClassSize().start)
