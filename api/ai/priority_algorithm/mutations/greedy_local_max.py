from typing import List, Dict

from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.priority_algorithm.mutations.interfaces import Mutation
from api.ai.priority_algorithm.mutations.utils import (
    get_available_priority_teams,
    score,
)
from api.ai.priority_algorithm.priority.interfaces import Priority
from api.dataclasses.student import Student
import random


class GreedyLocalMaxMutation(Mutation):
    def __init__(self, number_of_teams: int = 2):
        super().__init__()
        self.number_of_teams = number_of_teams

    def validate(self):
        if self.number_of_teams < 2:
            raise ValueError("Greedy local max must swap between at least 2 teams")

    def mutate_one(
        self,
        priority_team_set: PriorityTeamSet,
        priorities: List[Priority],
        student_dict: Dict[int, Student],
        team_generation_options: TeamGenerationOptions,
    ):
        """
        1. Pick two random teams
        2. Pool all students of the two team together
        3. Add each student from pool back into two new pools by doing the following for each student in the pool
            - If one of the pools is full add student to not full pool, else
            - Add student to each pool and get score of each pool, keeping the student in the pool whose score increases the most
        """
        available_priority_teams: List[PriorityTeam] = get_available_priority_teams(
            priority_team_set
        )
        try:
            if len(available_priority_teams) < self.number_of_teams:
                return priority_team_set
            teams = random.sample(available_priority_teams, self.number_of_teams)
            team_sizes = [len(team.student_ids) for team in teams]
            students = [student_id for team in teams for student_id in team.student_ids]
            random.shuffle(students)
            mutated_teams = [[] for _ in range(self.number_of_teams)]
            scores = [0 for _ in range(self.number_of_teams)]
            for student in students:
                max_index = None
                max_score_increase = None
                for i, mutated_team in enumerate(mutated_teams):
                    # Check if there's space
                    if len(mutated_team) >= team_sizes[i]:
                        continue

                    # Try adding student to team
                    teams[i].student_ids = mutated_team + [student]
                    updated_score = score(teams[i], priorities, student_dict)

                    # Track which team benefits the most from the added student
                    if (
                        max_index is None
                        or max_score_increase < updated_score - scores[i]
                    ):
                        max_index = i
                        max_score_increase = updated_score - scores[i]

                # Permanently add student to team the benefited the most
                mutated_teams[max_index].append(student)
                scores[max_index] += max_score_increase

            # Set each team's students to the newly formed teams
            for i, team in enumerate(teams):
                team.student_ids = mutated_teams[i]
        except ValueError:
            return priority_team_set
        return priority_team_set
