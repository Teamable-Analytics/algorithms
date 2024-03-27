from typing import List, Dict, Tuple

from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations import utils
from api.ai.priority_algorithm.mutations.interfaces import Mutation
from api.ai.priority_algorithm.mutations.robinhood import (
    valid_robinhood_arguments,
    perform_local_max_portion_of_robinhood,
)
from api.ai.priority_algorithm.mutations.utils import get_available_priority_teams
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student


class RobinhoodHolisticMutation(Mutation):
    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        min_team_size: int,
        max_team_size: int,
    ) -> PriorityTeamSet:
        """
        This is a variation of mutate_robinhood that does not consider individual priorities. Instead, it considers the entire set of priorities as a whole. This is done by calculating the score of each team in the team set, and then performing the local max portion of the robinhood mutation on the team with the lowest score and the team with the highest score.
        """

        if not valid_robinhood_arguments(priority_team_set, priorities, student_dict):
            return priority_team_set

        cloned_priority_team_set: PriorityTeamSet = priority_team_set.clone()

        available_priority_teams = get_available_priority_teams(
            cloned_priority_team_set
        )

        # Calculate the score of each team in the team set
        team_scores: List[Tuple[PriorityTeam, int]] = []
        for team in available_priority_teams:
            team_scores.append((team, utils.score(team, priorities, student_dict)))

        # Find the min and max scores
        min_scoring_team: Tuple[PriorityTeam, int] = min(
            team_scores, key=lambda x: x[1]
        )
        team_scores.remove(min_scoring_team)
        max_scoring_team: Tuple[PriorityTeam, int] = max(
            team_scores, key=lambda x: x[1]
        )

        # Perform local max portion of robinhood
        team_set, score = perform_local_max_portion_of_robinhood(
            cloned_priority_team_set,
            priorities,
            student_dict,
            min_scoring_team[0],
            max_scoring_team[0],
        )

        return team_set
