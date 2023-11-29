import dataclasses
from typing import List, Type

from api.ai.interfaces.algorithm_options import (
    AnyAlgorithmOptions,
    RandomAlgorithmOptions,
    PriorityAlgorithmOptions,
    SocialAlgorithmOptions,
    WeightAlgorithmOptions,
    MultipleRoundRobinAlgorithmOptions,
    DoubleRoundRobinAlgorithmOptions, GeneralizedEnvyGraphAlgorithmOptions,
)
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.models.enums import (
    AlgorithmType,
    DiversifyType,
    RelationshipBehaviour,
)
from api.models.team import TeamShell
from benchmarking.evaluations.enums import PreferenceSubject
from benchmarking.evaluations.goals import (
    WeightGoal,
    PreferenceGoal,
    DiversityGoal,
    ProjectRequirementGoal, ProjectsGoal,
)
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.simulation.goal_to_priority import (
    goal_to_priority,
)
from utils.dictionaries import prune_dictionary_keys


class MockAlgorithm:
    @staticmethod
    def get_team_generation_options(
        num_students: int, num_teams: int, initial_teams: List[TeamShell] = None
    ) -> TeamGenerationOptions:
        _num_teams = len(initial_teams) if initial_teams else num_teams
        min_team_size = num_students // _num_teams
        max_team_size = (
            min_team_size if num_students % _num_teams == 0 else min_team_size + 1
        )
        return TeamGenerationOptions(
            max_team_size=max_team_size,
            min_team_size=min_team_size,
            total_teams=_num_teams,
            initial_teams=initial_teams,
        )

    @staticmethod
    def algorithm_options_class(
        algorithm_type: AlgorithmType,
    ) -> Type[AnyAlgorithmOptions]:
        if algorithm_type == AlgorithmType.RANDOM:
            return RandomAlgorithmOptions
        if algorithm_type == AlgorithmType.WEIGHT:
            return WeightAlgorithmOptions
        if algorithm_type == AlgorithmType.SOCIAL:
            return SocialAlgorithmOptions
        if algorithm_type == AlgorithmType.PRIORITY:
            return PriorityAlgorithmOptions
        if algorithm_type == AlgorithmType.MRR:
            return MultipleRoundRobinAlgorithmOptions
        if algorithm_type == AlgorithmType.DRR:
            return DoubleRoundRobinAlgorithmOptions
        if algorithm_type == AlgorithmType.GEG:
            return GeneralizedEnvyGraphAlgorithmOptions

    @staticmethod
    def field_names_for_algorithm_type_options(
        algorithm_type: AlgorithmType,
    ) -> List[str]:
        algorithm_options_cls = MockAlgorithm.algorithm_options_class(algorithm_type)
        return [_.name for _ in dataclasses.fields(algorithm_options_cls)]

    @staticmethod
    def extract_priorities_from_goals(goals: List[Goal]) -> List[Priority]:
        priorities = []
        for goal in goals:
            try:
                priorities.append(goal_to_priority(goal))
            except NotImplementedError:
                continue

        return priorities

    @staticmethod
    def algorithm_options_from_scenario(
        algorithm_type: AlgorithmType, scenario: Scenario, max_project_preferences: int
    ) -> AnyAlgorithmOptions:
        kwargs = {}
        attributes_to_diversify = []
        attributes_to_concentrate = []
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
                    kwargs.update({"friend_behaviour": RelationshipBehaviour.ENFORCE})
                if goal.subject == PreferenceSubject.ENEMIES:
                    kwargs.update({"enemy_behaviour": RelationshipBehaviour.ENFORCE})
            if isinstance(goal, DiversityGoal):
                if goal.strategy == DiversifyType.DIVERSIFY:
                    attributes_to_diversify.append(goal.attribute)
                else:
                    attributes_to_concentrate.append(goal.attribute)
            if isinstance(goal, ProjectRequirementGoal):
                has_project_requirement_goal = True
            if isinstance(goal, ProjectsGoal):
                kwargs.update({"projects": goal.projects})

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

        priorities = MockAlgorithm.extract_priorities_from_goals(
            [goal for goal in scenario.goals]
        )
        kwargs.update(
            {
                "max_project_preferences": max_project_preferences,
                "attributes_to_concentrate": attributes_to_concentrate,
                "attributes_to_diversify": attributes_to_diversify,
                "priorities": priorities,
            }
        )

        algorithm_options_class = MockAlgorithm.algorithm_options_class(algorithm_type)
        specific_kwargs = prune_dictionary_keys(
            kwargs,
            MockAlgorithm.field_names_for_algorithm_type_options(algorithm_type),
        )
        # create an instance of the correct AlgorithmOptions class with only the keys relevant to it
        return algorithm_options_class(**specific_kwargs)
