from typing import List

from api.ai.priority_algorithm.priority_algorithm import (
    PriorityAlgorithm as PriorityAlgorithmNew,
)
from benchmarking.evaluations.enums import PreferenceSubject
from benchmarking.evaluations.goals import (
    WeightGoal,
    PreferenceGoal,
    DiversityGoal,
    ProjectRequirementGoal,
)
from benchmarking.evaluations.interfaces import Scenario
from benchmarking.simulation.algorithm_translator import AlgorithmTranslator
from api.models.enums import (
    AlgorithmType,
    DiversifyType,
)
from api.models.team import Team
from api.models.team_set import TeamSet
from old.team_formation.app.team_generator.algorithm.algorithms import (
    AlgorithmOptions,
    RandomAlgorithm,
    WeightAlgorithm,
)
from old.team_formation.app.team_generator.algorithm.priority_algorithm.priority_algorithm import (
    PriorityAlgorithm,
)
from old.team_formation.app.team_generator.algorithm.social_algorithm.social_algorithm import (
    SocialAlgorithm,
)
from old.team_formation.app.team_generator.student import Student as AlgorithmStudent
from old.team_formation.app.team_generator.team_generator import (
    TeamGenerationOption,
    TeamGenerator,
)


class MockAlgorithm:
    def __init__(
            self,
            algorithm_type: AlgorithmType,
            team_generation_options: TeamGenerationOption,
            algorithm_options: AlgorithmOptions,
    ):
        self.algorithm = MockAlgorithm.get_algorithm_from_type(
            algorithm_type, algorithm_options
        )
        self.team_generation_options = team_generation_options

    def generate(self, students: List[AlgorithmStudent]) -> TeamSet:
        team_generator = TeamGenerator(
            students, self.algorithm, [], self.team_generation_options
        )
        teams = team_generator.generate()
        return AlgorithmTranslator.algorithm_teams_to_team_set(teams)

    @staticmethod
    def get_algorithm_from_type(
            algorithm_type: AlgorithmType, algorithm_options: AlgorithmOptions
    ):
        if algorithm_type == AlgorithmType.RANDOM:
            return RandomAlgorithm(algorithm_options)
        if algorithm_type == AlgorithmType.WEIGHT:
            return WeightAlgorithm(algorithm_options)
        if algorithm_type == AlgorithmType.SOCIAL:
            return SocialAlgorithm(algorithm_options)
        if algorithm_type == AlgorithmType.PRIORITY:
            return PriorityAlgorithm(algorithm_options)
        if algorithm_type == AlgorithmType.PRIORITY_NEW:
            return PriorityAlgorithmNew(algorithm_options)

    @staticmethod
    def get_team_generation_options(
            num_students: int, num_teams: int, initial_teams: List[Team] = None
    ) -> TeamGenerationOption:
        if initial_teams:
            return AlgorithmTranslator.initial_teams_to_team_generation_options(
                initial_teams,
                num_students=num_students,
            )

        min_team_size = num_students // num_teams
        return TeamGenerationOption(
            max_team_size=min_team_size + 1,
            min_team_size=min_team_size,
            total_teams=num_teams,
            team_options=[],
        )

    @staticmethod
    def algorithm_options_from_scenario(
            algorithm_type: AlgorithmType, scenario: Scenario, max_project_preferences: int
    ) -> AlgorithmOptions:
        kwargs = {}
        diversify_options = []
        concentrate_options = []
        priorities = []

        has_weight_goal = False
        has_project_requirement_goal = False
        has_project_preference_goal = False
        for goal in scenario.goals:
            if isinstance(goal, WeightGoal):
                kwargs.update(
                    {
                        "requirement_weight": goal.project_requirement_weight,
                        "social_weight": goal.social_preference_weight,
                        "diversity_weight": goal.diversity_goal_weight,
                        "preference_weight": goal.project_preference_weight,
                    }
                )
                has_weight_goal = True
            if isinstance(goal, PreferenceGoal):
                if goal.subject == PreferenceSubject.PROJECTS:
                    has_project_preference_goal = True
                if goal.subject == PreferenceSubject.FRIENDS:
                    kwargs.update({"whitelist_behaviour": "enforce"})
                if goal.subject == PreferenceSubject.ENEMIES:
                    kwargs.update({"blacklist_behaviour": "enforce"})
            if isinstance(goal, DiversityGoal):
                if goal.strategy == DiversifyType.DIVERSIFY:
                    diversify_options.append({"id": goal.attribute})
                else:
                    concentrate_options.append({"id": goal.attribute})
                priority = (
                    AlgorithmTranslator.diversity_goal_to_algorithm_priority_dict(goal)
                )
                if priority:
                    priorities.append(priority)
            if isinstance(goal, ProjectRequirementGoal):
                has_project_requirement_goal = goal.match_skills

        if not has_weight_goal:
            # set default weights if no weights are explicitly given in the scenario
            if algorithm_type == AlgorithmType.WEIGHT:
                kwargs.update(
                    {
                        "requirement_weight": 1 + int(has_project_requirement_goal),
                        "social_weight": 1 + int(has_project_preference_goal),
                        "diversity_weight": 1,
                        "preference_weight": 1,
                    }
                )
            if algorithm_type == AlgorithmType.PRIORITY:
                kwargs.update(
                    {
                        "requirement_weight": 0,
                        "social_weight": 0,
                        "diversity_weight": 1,
                        "preference_weight": 0,
                    }
                )

            if algorithm_type == AlgorithmType.SOCIAL:
                kwargs.update({"social_weight": 1})

        return AlgorithmOptions(
            **kwargs,
            max_project_preferences=max_project_preferences,
            concentrate_options=concentrate_options,
            diversify_options=diversify_options,
            priorities=priorities,
        )
