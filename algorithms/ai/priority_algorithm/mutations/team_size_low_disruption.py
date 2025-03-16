from typing import List, Dict, Tuple

import numpy as np

from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.ai.priority_algorithm.custom_dataclasses import (
    PriorityTeamSet,
    PriorityTeam,
)
from algorithms.ai.priority_algorithm.mutations.interfaces import Mutation
from algorithms.ai.priority_algorithm.mutations.utils import (
    get_available_priority_teams,
)
from algorithms.ai.priority_algorithm.priority.interfaces import Priority
from algorithms.dataclasses.student import Student


class TeamSizeLowDisruptionMutation(Mutation):
    """
    Mutation to adjust team sizes within the bounds.

    The idea is to first randomly generate the sizes of the new teams (with approx uniform distribution).
    Then, only move students from teams with too many students to teams with not enough students.
    This minimizes the change in teams and hopefully won't tear apart teams that are doing well.
    """

    def __init__(self, num_teams: int = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_teams = num_teams

    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ) -> PriorityTeamSet:
        available_priority_teams: List[PriorityTeam] = get_available_priority_teams(
            priority_team_set
        )
        try:
            if len(available_priority_teams) < self.num_teams:
                return priority_team_set

            selected_teams = [
                available_priority_teams[i]
                for i in np.random.choice(
                    len(available_priority_teams), self.num_teams, replace=False
                )
            ]

            new_sizes = get_sizes(
                len(selected_teams),
                sum([len(team.student_ids) for team in selected_teams]),
                team_generation_options.min_team_size,
                team_generation_options.max_team_size,
            )

            # Sort teams into those which need to shrink, need to grow, and are the right size
            shrinking_teams: List[Tuple[int, PriorityTeam]] = []
            growing_teams: List[Tuple[int, PriorityTeam]] = []
            done_teams: List[PriorityTeam] = []
            for size, team in zip(new_sizes, selected_teams):
                if len(team.student_ids) > size:
                    shrinking_teams.append((size, team))
                elif len(team.student_ids) < size:
                    growing_teams.append((size, team))
                else:
                    done_teams.append(team)

            # Move students from oversized teams to undersized teams
            for target_size, growing_team in growing_teams:
                while len(growing_team.student_ids) < target_size:
                    # Grab a random student from the last team in the shrinking teams
                    shrink_target, shrinking_team = shrinking_teams[0]
                    growing_team.student_ids.append(
                        shrinking_team.student_ids.pop(
                            np.random.randint(len(shrinking_team.student_ids))
                        )
                    )
                    if len(shrinking_team.student_ids) == shrink_target:
                        # Move shrinking team to done
                        done_teams.append(shrinking_team)
                        shrinking_teams.pop(0)
                done_teams.append(growing_team)
        except ValueError:
            return priority_team_set
        return priority_team_set


def get_sizes(
    num_teams: int, num_students: int, min_size: int, max_size: int
) -> List[int]:
    """
    Generates a list of team sizes
    """
    sizes = [np.random.randint(min_size, max_size + 1) for _ in range(num_teams)]
    diff = num_students - sum(sizes)
    if diff < 0:
        # If the teams sizes are bigger than the number of students
        for _ in range(abs(diff)):
            index = np.random.randint(num_teams)
            while sizes[index] <= min_size:
                index = np.random.randint(num_teams)
            sizes[index] -= 1
    elif diff > 0:
        # If the teams sizes are smaller than the number of students
        for _ in range(diff):
            index = np.random.randint(num_teams)
            while sizes[index] >= max_size:
                index = np.random.randint(num_teams)
            sizes[index] += 1
    return sizes
