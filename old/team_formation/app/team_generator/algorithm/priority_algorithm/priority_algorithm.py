import random
import time
from typing import Dict, List

from old.team_formation.app.team_generator.algorithm.algorithms import WeightAlgorithm
from old.team_formation.app.team_generator.algorithm.priority_algorithm.priority import (
    Priority,
)
from old.team_formation.app.team_generator.algorithm.priority_algorithm.priority_teamset import (
    PriorityTeamSet,
    PriorityTeam,
)
from old.team_formation.app.team_generator.student import Student
from old.team_formation.app.team_generator.team import Team
from old.team_formation.app.team_generator.team_generator import TeamGenerationOption


class PriorityAlgorithm(WeightAlgorithm):
    """Class used to select teams using a priority algorithm."""

    MAX_KEEP: int = 3  # nodes
    MAX_SPREAD: int = 3  # nodes
    MAX_ITERATE: int = 1000  # times
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
        for priority in self.options.priorities:
            priorities.append(
                Priority(
                    constraint=priority["constraint"],
                    skill_id=priority["skill_id"],
                    limit_option=priority["limit_option"],
                    limit=priority["limit"],
                    value=priority["value"],
                )
            )
        return priorities

    def generate_initial_teams(
        self,
        students: List[Student],
        teams: List[Team],
        team_generation_option: TeamGenerationOption,
    ) -> PriorityTeamSet:
        self.set_default_weights()
        initial_teams = super().generate(students, teams, team_generation_option)
        priority_teams: List[PriorityTeam] = []
        for team in initial_teams:
            priority_team = PriorityTeam(
                team=team, student_ids=[student.id for student in team.students]
            )
            priority_teams.append(priority_team)
        return PriorityTeamSet(priority_teams=priority_teams)

    def generate(
        self,
        students: List[Student],
        teams: List[Team],
        team_generation_option: TeamGenerationOption,
    ) -> List[Team]:
        """
        Generate teams using a priority algorithm.
        """
        self.students = students
        self.student_dict = self.create_student_dict(students)
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
            # print(f'Iteration: {iteration} | {[team_set.score for team_set in team_sets]}')
            iteration += 1

        # print(f'Total iterations: {iteration}')
        # print(f'Scores: {[team_set.score for team_set in team_sets]}')
        return self.save_team_compositions_to_teams(team_sets[0])

    def save_team_compositions_to_teams(
        self, priority_team_set: PriorityTeamSet
    ) -> List[Team]:
        teams: List[Team] = []
        self.empty_all_teams(
            [priority_team.team for priority_team in priority_team_set.priority_teams]
        )
        for priority_team in priority_team_set.priority_teams:
            students = [
                self.student_dict[student_id]
                for student_id in priority_team.student_ids
            ]
            self.save_students_to_team(priority_team.team, students)
            teams.append(priority_team.team)
        return teams

    def empty_all_teams(self, teams: List[Team]):
        for team in teams:
            team.empty()
        for student in self.students:
            student.team = None

    def mutate_team_random(self, team_set: PriorityTeamSet) -> PriorityTeamSet:
        """
        Note, both teams must not be empty
        Actually modifies the team_set passed
        """
        available_priority_teams = [
            priority_team
            for priority_team in team_set.priority_teams
            if not priority_team.team.is_locked
        ]
        try:
            team1, team2 = random.sample(available_priority_teams, 2)
            student_1_id: int = random.choice(team1.student_ids)
            student_2_id: int = random.choice(team2.student_ids)
            self.swap_student_between_teams(team1, student_1_id, team2, student_2_id)
        except ValueError:
            return team_set
        return team_set

    def mutate(self, team_set: PriorityTeamSet) -> List[PriorityTeamSet]:
        """
        Mutate a single teamset into child teamsets
        """
        cloned_team_sets = [
            team_set.clone() for _ in range(PriorityAlgorithm.MAX_SPREAD)
        ]
        return [
            self.mutate_team_random(cloned_team_set)
            for cloned_team_set in cloned_team_sets
        ]

    def swap_student_between_teams(
        self,
        team1: PriorityTeam,
        student_1_id: int,
        team2: PriorityTeam,
        student_2_id: int,
    ):
        team1.student_ids.remove(student_1_id)
        team1.student_ids.append(student_2_id)

        team2.student_ids.remove(student_2_id)
        team2.student_ids.append(student_1_id)
