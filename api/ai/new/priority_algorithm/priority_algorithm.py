import time
from typing import cast, Dict, List

from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.new.interfaces.algorithm_options import (
    PriorityAlgorithmOptions,
    WeightAlgorithmOptions,
)
from api.ai.new.priority_algorithm.custom_models import PriorityTeamSet, PriorityTeam
from api.ai.new.priority_algorithm.mutations.local_max import mutate_local_max
from api.ai.new.priority_algorithm.mutations.random_swap import mutate_random_swap
from api.ai.new.priority_algorithm.mutations.robinhood import (
    mutate_robinhood,
    mutate_robinhood_holistic,
)
from api.ai.new.utils import save_students_to_team
from api.ai.new.weight_algorithm.weight_algorithm import WeightAlgorithm
from api.models.student.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet

DEFAULT_PRIORITY_ALGORITHM_CONFIG = PriorityAlgorithmConfig(
    MAX_KEEP=3,
    MAX_SPREAD=3,
    MAX_ITERATE=1500,
    MAX_TIME=1,
)


class PriorityAlgorithm(Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: PriorityAlgorithmOptions = cast(
            PriorityAlgorithmOptions, self.algorithm_options
        )
        if self.algorithm_config:
            self.algorithm_config: PriorityAlgorithmConfig = cast(
                PriorityAlgorithmConfig, self.algorithm_config
            )
        else:
            self.algorithm_config = DEFAULT_PRIORITY_ALGORITHM_CONFIG

        self.student_dict: Dict[int, Student] = {}

    def generate_initial_team_set(
        self,
        students: List[Student],
    ) -> PriorityTeamSet:
        team_set = WeightAlgorithm(
            # todo: implement proper conversion from priority algorithm options to weight algorithm options
            algorithm_options=weight_options_from_priority_options(
                self.algorithm_options
            ),
            team_generation_options=self.team_generation_options,
        ).generate(students)

        # keep internal self.teams accurate
        self.teams = team_set.teams

        return PriorityTeamSet(
            priority_teams=[
                PriorityTeam(team=team, student_ids=[s.id for s in team.students])
                for team in team_set.teams
            ]
        )

    def generate(self, students: List[Student]) -> TeamSet:
        self.student_dict = create_student_dict(students)

        start_time = time.time()
        iteration = 0
        team_sets = [self.generate_initial_team_set(students)]

        while (
            time.time() - start_time < self.algorithm_config.MAX_TIME
            and iteration < self.algorithm_config.MAX_ITERATE
        ):
            new_team_sets: List[PriorityTeamSet] = []
            for team_set in team_sets:
                new_team_sets += self.mutate(team_set)
            team_sets = new_team_sets + team_sets
            team_sets = sorted(
                team_sets,
                key=lambda ts: ts.calculate_score(
                    self.algorithm_options.priorities, self.student_dict
                ),
                reverse=True,
            )
            team_sets = team_sets[: self.algorithm_config.MAX_KEEP]
            iteration += 1

        # the first team set is the "best" one
        return self._unpack_priority_team_set(team_sets[0])

    def mutate(self, team_set: PriorityTeamSet) -> List[PriorityTeamSet]:
        """
        Mutate a single teamset into child teamsets
        """
        algorithm = 1
        cloned_team_sets = [
            team_set.clone() for _ in range(self.algorithm_config.MAX_SPREAD)
        ]
        if algorithm == 1:
            return [
                mutate_random_swap(cloned_team_set)
                for cloned_team_set in cloned_team_sets
            ]
        elif algorithm == 2:
            return [
                mutate_robinhood(
                    cloned_team_set,
                    self.algorithm_options.priorities,
                    self.student_dict,
                )
                for cloned_team_set in cloned_team_sets
            ]
        elif algorithm == 3:
            return [
                mutate_robinhood_holistic(
                    cloned_team_set,
                    self.algorithm_options.priorities,
                    self.student_dict,
                )
                for cloned_team_set in cloned_team_sets
            ]
        elif algorithm == 4:
            return [
                mutate_local_max(
                    cloned_team_sets[0],
                    self.algorithm_options.priorities,
                    self.student_dict,
                ),
                *[
                    mutate_random_swap(cloned_team_set)
                    for cloned_team_set in cloned_team_sets[1:]
                ],
            ]

    def _unpack_priority_team_set(self, priority_team_set: PriorityTeamSet) -> TeamSet:
        teams: List[Team] = []

        # empty underlying teams
        for priority_team in priority_team_set.priority_teams:
            priority_team.team.empty()

        # students will be assigned a .team from the generate_initial_teams(), this must be removed
        for student in self.student_dict.values():
            student.team = None

        for priority_team in priority_team_set.priority_teams:
            students = [
                self.student_dict[student_id]
                for student_id in priority_team.student_ids
            ]
            save_students_to_team(priority_team.team, students)
            teams.append(priority_team.team)

        return TeamSet(teams=teams)


def create_student_dict(students: List[Student]) -> Dict[int, Student]:
    student_dict = {}
    for student in students:
        student_dict[student.id] = student
    return student_dict


def weight_options_from_priority_options(
    options: PriorityAlgorithmOptions,
) -> WeightAlgorithmOptions:
    return WeightAlgorithmOptions(
        requirement_weight=options.requirement_weight,
        social_weight=options.social_weight,
        diversity_weight=options.diversity_weight,
        preference_weight=options.preference_weight,
        max_project_preferences=options.max_project_preferences,
        friend_behaviour=options.friend_behaviour,
        enemy_behaviour=options.enemy_behaviour,
        attributes_to_diversify=options.attributes_to_diversify,
        attributes_to_concentrate=options.attributes_to_concentrate,
    )
