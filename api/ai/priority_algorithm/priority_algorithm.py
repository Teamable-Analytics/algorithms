import time
from typing import Dict, List, Literal

from api.ai.priority_algorithm.interfaces import Priority
from api.ai.priority_algorithm.mutations.local_max import mutate_local_max
from api.ai.priority_algorithm.mutations.random_swap import mutate_random_swap
from api.ai.priority_algorithm.mutations.robinhood import mutate_robinhood
from api.ai.priority_algorithm.priority import TokenizationPriority
from api.ai.priority_algorithm.priority_teamset import PriorityTeamSet, PriorityTeam
from benchmarking.simulation.algorithm_translator import AlgorithmTranslator
from api.models.enums import DiversifyType, TokenizationConstraintDirection
from api.models.student import Student
from api.models.team import Team
from old.team_formation.app.team_generator.algorithm.algorithms import WeightAlgorithm
from old.team_formation.app.team_generator.student import Student as AlgorithmStudent
from old.team_formation.app.team_generator.team import Team as AlgorithmTeam
from old.team_formation.app.team_generator.team_generator import TeamGenerationOption


class PriorityAlgorithm(WeightAlgorithm):
    """Class used to select teams using a priority algorithm."""

    MAX_KEEP: int = 3  # nodes
    MAX_SPREAD: int = 3  # nodes
    MAX_ITERATE: int = 1500  # times
    MAX_TIME: int = 1  # seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_dict: Dict[int, Student] = {}
        self.priorities: List[Priority] = []
        self.students: List[Student] = []

    def set_default_weights(self):
        self.options.diversity_weight = 1
        self.options.preference_weight = 1
        self.options.requirement_weight = 1
        self.options.social_weight = 1

    def create_student_dict(self, students: List[Student]) -> Dict[int, Student]:
        student_dict = {}
        for student in students:
            student_dict[student.id] = student
        return student_dict

    def create_priority_objects(self) -> List[Priority]:
        priorities = []

        # todo: depends on the input dictionary object structure,
        #  would be better if the input dict just had the right types
        def get_strategy(constraint: Literal["diversify", "concentrate"]):
            if constraint == "diversify":
                return DiversifyType.DIVERSIFY
            if constraint == "concentrate":
                return DiversifyType.CONCENTRATE
            raise TypeError

        def get_direction(limit_option: Literal["min_of", "max_of"]):
            if limit_option == "min_of":
                return TokenizationConstraintDirection.MIN_OF
            if limit_option == "max_of":
                return TokenizationConstraintDirection.MAX_OF
            raise TypeError

        for priority in self.options.priorities:
            priorities.append(
                # todo: currently, only tokenization priorities are supported
                TokenizationPriority(
                    attribute_id=priority["skill_id"],
                    strategy=get_strategy(priority["constraint"]),
                    direction=get_direction(priority["limit_option"]),
                    threshold=priority["limit"],
                    value=priority["value"],
                )
            )
        return priorities

    def generate_initial_teams(
        self,
        students: List[AlgorithmStudent],
        teams: List[AlgorithmTeam],
        team_generation_option: TeamGenerationOption,
    ) -> PriorityTeamSet:
        self.set_default_weights()
        initial_teams = super().generate(students, teams, team_generation_option)
        initial_team_set = AlgorithmTranslator.algorithm_teams_to_team_set(
            initial_teams
        )
        priority_teams: List[PriorityTeam] = []
        for team in initial_team_set.teams:
            priority_team = PriorityTeam(
                team=team, student_ids=[student.id for student in team.students]
            )
            priority_teams.append(priority_team)

        return PriorityTeamSet(priority_teams=priority_teams)

    def generate(
        self,
        students: List[AlgorithmStudent],
        teams: List[AlgorithmTeam],
        team_generation_option: TeamGenerationOption,
    ) -> List[AlgorithmTeam]:
        self.students = AlgorithmTranslator.algorithm_students_to_students(students)
        self.student_dict = self.create_student_dict(self.students)
        self.priorities = self.create_priority_objects()
        start_time = time.time()
        iteration = 0
        team_sets = [
            self.generate_initial_teams(students, teams, team_generation_option)
        ]

        while (
            time.time() - start_time
        ) < self.MAX_TIME and iteration < self.MAX_ITERATE:
            new_team_sets: List[PriorityTeamSet] = []
            for team_set in team_sets:
                new_team_sets += self.mutate(team_set)
            team_sets = new_team_sets + team_sets
            team_sets = sorted(
                team_sets,
                key=lambda ts: ts.calculate_score(self.priorities, self.student_dict),
                reverse=True,
            )
            team_sets = team_sets[: self.MAX_KEEP]
            iteration += 1
        return AlgorithmTranslator.teams_to_algorithm_teams(
            self.save_team_compositions_to_teams(team_sets[0])
        )

    def save_team_compositions_to_teams(
        self, priority_team_set: PriorityTeamSet
    ) -> List[Team]:
        teams: List[Team] = []

        # empty underlying teams
        for priority_team in priority_team_set.priority_teams:
            priority_team.team.empty()

        for priority_team in priority_team_set.priority_teams:
            students = [
                self.student_dict[student_id]
                for student_id in priority_team.student_ids
            ]
            self.save_students_to_team(priority_team.team, students)
            teams.append(priority_team.team)
        return teams

    def mutate(self, team_set: PriorityTeamSet) -> List[PriorityTeamSet]:
        """
        Mutate a single teamset into child teamsets
        """
        algorithm = 1
        cloned_team_sets = [
            team_set.clone() for _ in range(PriorityAlgorithm.MAX_SPREAD)
        ]
        if algorithm == 1:
            return [
                mutate_random_swap(cloned_team_set)
                for cloned_team_set in cloned_team_sets
            ]
        elif algorithm == 2:
            return [
                mutate_robinhood(cloned_team_set, self.priorities, self.student_dict)
                for cloned_team_set in cloned_team_sets
            ]
        elif algorithm == 3:
            return [
                mutate_local_max(
                    cloned_team_sets[0], self.priorities, self.student_dict
                ),
                *[
                    mutate_random_swap(cloned_team_set)
                    for cloned_team_set in cloned_team_sets[1:]
                ],
            ]
