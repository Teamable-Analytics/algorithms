import time
from typing import cast, Dict, List

from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
)
from api.ai.interfaces.algorithm_options import (
    PriorityAlgorithmOptions,
    WeightAlgorithmOptions,
    RandomAlgorithmOptions,
)
from api.ai.priority_algorithm.custom_dataclasses import PriorityTeamSet, PriorityTeam
from api.ai.random_algorithm.random_algorithm import RandomAlgorithm
from api.ai.utils import save_students_to_team
from api.ai.weight_algorithm.weight_algorithm import WeightAlgorithm
from api.dataclasses.student import Student
from api.dataclasses.team import Team
from api.dataclasses.team_set import TeamSet


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
            self.algorithm_config = PriorityAlgorithmConfig()

        self.student_dict: Dict[int, Student] = {}

    def generate_initial_team_set(
        self,
        students: List[Student],
    ) -> PriorityTeamSet:
        if self.algorithm_config.START_TYPE == PriorityAlgorithmStartType.RANDOM:
            team_set = RandomAlgorithm(
                algorithm_options=RandomAlgorithmOptions(),
                team_generation_options=self.team_generation_options,
            ).generate(students)
        elif self.algorithm_config.START_TYPE == PriorityAlgorithmStartType.WEIGHT:
            team_set = WeightAlgorithm(
                algorithm_options=weight_options_from_priority_options(
                    self.algorithm_options
                ),
                team_generation_options=self.team_generation_options,
            ).generate(students)
        else:
            # This shouldn't trigger unless user intentionally sets it to None because the config has a default value set
            raise ValueError("Priority algorithm start type must be set")

        return PriorityTeamSet(
            priority_teams=[
                PriorityTeam(
                    team_shell=team.to_shell(),
                    student_ids=[s.id for s in team.students],
                )
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
        mutated_team_sets = []
        for mutation_func, num_outputs in self.algorithm_config.MUTATIONS:
            mutated_team_sets.extend(
                [
                    mutation_func(
                        team_set.clone(),
                        self.algorithm_options.priorities,
                        self.student_dict,
                    )
                    for _ in range(num_outputs)
                ]
            )

        return mutated_team_sets

    def _unpack_priority_team_set(self, priority_team_set: PriorityTeamSet) -> TeamSet:
        teams: List[Team] = []

        # students will be assigned a .team from the generate_initial_teams(), this must be removed
        for student in self.student_dict.values():
            student.team = None

        for priority_team in priority_team_set.priority_teams:
            students = [
                self.student_dict[student_id]
                for student_id in priority_team.student_ids
            ]
            team = Team.from_shell(priority_team.team_shell)
            save_students_to_team(team, students)
            teams.append(team)

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
