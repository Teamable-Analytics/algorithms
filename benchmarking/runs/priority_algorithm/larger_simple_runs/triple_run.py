import re
from typing import Dict, Tuple, List

import numpy as np
import typer
from matplotlib import pyplot as plt

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.models.enums import (
    AlgorithmType,
    RequirementsCriteria,
    DiversifyType,
    ScenarioAttribute,
    TokenizationConstraintDirection,
    Gender,
)
from api.models.tokenization_constraint import TokenizationConstraint
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.evaluations.enums import PreferenceDirection, PreferenceSubject
from benchmarking.evaluations.goals import (
    PreferenceGoal,
    WeightGoal,
    ProjectRequirementGoal,
    DiversityGoal,
)
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.average_project_requirements_coverage import (
    AverageProjectRequirementsCoverage,
)
from benchmarking.evaluations.metrics.average_social_satisfied import (
    AverageSocialSatisfaction,
)
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineSimilarity
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.metrics.utils.team_calculations import (
    is_happy_team_1hp_friend,
    is_strictly_happy_team_friend,
)
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_projects import (
    get_custom_projects,
)
from benchmarking.runs.priority_algorithm.larger_simple_runs.custom_student_providers import (
    Major,
    Custom120SocialDiversityAndProjectStudentProvider,
)
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class TripleRun(Run):
    CLASS_SIZE = 120
    NUMBER_OF_TEAMS = 30
    NUMBER_OF_STUDENTS_PER_TEAM = 4

    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        # Ranges
        max_keep_range = [1] + list(range(5, 11, 5))
        max_spread_range = [1] + list(range(5, 11, 5))  # + [100]
        max_iterations_range = [1, 5]  # + [250]

        scenario = TripleScenario(
            max_num_friends=1,
            max_num_enemies=0,
            value_of_female=Gender.FEMALE.value,
            value_of_math=Major.MATH.value,
            value_of_21=21,
        )
        metrics = {
            "PrioritySatisfaction": PrioritySatisfaction(
                goals_to_priorities(scenario.goals),
                False,
            ),
            "AverageSocialSatisfaction": AverageSocialSatisfaction(
                metric_function=is_strictly_happy_team_friend
            ),
            "AverageCosineSimilarity": AverageCosineSimilarity(),
            "AverageProjectRequirementCoverage": AverageProjectRequirementsCoverage(),
        }
        initial_teams_provider = MockInitialTeamsProvider(
            settings=MockInitialTeamsProviderSettings(
                projects=get_custom_projects(),
            )
        )
        start_types = [
            PriorityAlgorithmStartType.WEIGHT,
            PriorityAlgorithmStartType.RANDOM,
        ]

        artifacts_dict = {start_type: {} for start_type in start_types}
        for start_type in start_types:
            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    scenario=scenario,
                    student_provider=Custom120SocialDiversityAndProjectStudentProvider(),
                    initial_teams_provider=initial_teams_provider,
                    cache_key=f"priority_algorithm/larger_simple_runs/class_size_120/triple_run/",
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_KEEP=max_keep,
                            MAX_SPREAD=max_spread,
                            MAX_ITERATE=max_iterations,
                            MAX_TIME=10000000,
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
            raise NotImplementedEro


class TripleScenario(Scenario):
    def __init__(
        self,
        max_num_friends: int,
        max_num_enemies: int,
        value_of_female: int,
        value_of_math: int,
        value_of_21: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.max_num_friends = max_num_friends
        self.max_num_enemies = max_num_enemies
        self.value_of_female = value_of_female
        self.value_of_math = value_of_math
        self.value_of_21 = value_of_21

    @property
    def name(self):
        return "Create teams that group social friends together after satisfying project requirements"

    @property
    def goals(self) -> List[Goal]:
        return [
            ProjectRequirementGoal(
                criteria=RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.GENDER.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_female,
                ),
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                ScenarioAttribute.AGE.value,
                tokenization_constraint=TokenizationConstraint(
                    direction=TokenizationConstraintDirection.MIN_OF,
                    threshold=2,
                    value=self.value_of_21,
                ),
            ),
            PreferenceGoal(
                PreferenceDirection.INCLUDE,
                PreferenceSubject.FRIENDS,
                max_num_friends=self.max_num_friends,
                max_num_enemies=self.max_num_enemies,
            ),
            WeightGoal(
                project_requirement_weight=3,
                diversity_goal_weight=2,
                social_preference_weight=1,
            ),
        ]


if __name__ == "__main__":
    typer.run(TripleRun().start)
