import time
from heapq import heappop, nlargest

from team_formation.app.team_generator.algorithm.algorithms import *
from team_formation.app.team_generator.algorithm.priority_algorithm.priority import Priority
from team_formation.app.team_generator.algorithm.priority_algorithm.priority_teamset import PriorityTeamSet
from team_formation.app.team_generator.team_generator import TeamGenerationOption


class PriorityAlgorithm(WeightAlgorithm):
    """Class used to select teams using a priority algorithm.
    """
    MAX_KEEP: int = 3  # nodes
    MAX_SPREAD: int = 3  # nodes
    MAX_ITERATE: int = 1500  # times
    MAX_TIME: int = 30  # seconds

    def set_default_weights(self):
        self.options.diversity_weight = 1
        self.options.preference_weight = 1
        self.options.requirement_weight = 1
        self.options.social_weight = 1

    def create_priority_objects(self) -> List[Priority]:
        priorities = []
        for priority in self.options.priorities:
            priorities.append(
                Priority(
                    constraint=priority['constraint'],
                    skill_id=priority['skill_id'],
                    limit_option=priority['limit_option'],
                    limit=priority['limit'],
                    value=priority['value']
                )
            )
        return priorities

    def generate_initial_teams(self, students: List[Student], teams: List[Team],
                               team_generation_option: TeamGenerationOption) -> PriorityTeamSet:
        self.set_default_weights()
        priorities = self.create_priority_objects()
        initial_teams = super().generate(students, teams, team_generation_option)
        return PriorityTeamSet(teams=initial_teams, priorities=priorities)

    def generate(self, students: List[Student], teams: List[Team],
                 team_generation_option: TeamGenerationOption) -> List[Team]:
        """
        Generate teams using a priority algorithm.
        """
        start_time = time.time()
        iteration = 0
        team_sets = [self.generate_initial_teams(students, teams, team_generation_option)]

        while (time.time() - start_time) < self.MAX_TIME and iteration < self.MAX_ITERATE:
            new_team_sets: List[PriorityTeamSet] = []
            for team_set in team_sets:
                new_team_sets += self.mutate(team_set)
            team_sets = new_team_sets + team_sets
            team_sets = nlargest(self.MAX_KEEP, team_sets)
            print([team_set.score for team_set in team_sets])
            iteration += 1

        return heappop(team_sets).teams

    def mutate_team_random(self, team_set: PriorityTeamSet) -> PriorityTeamSet:
        """
        Note, both teams must not be empty
        Actually modifies the team_set passed
        """
        available_teams = [team for team in team_set.teams if not team.is_locked]
        try:
            team1, team2 = random.sample(available_teams, 2)
            student_team1 = random.choice(team1.students)
            student_team2 = random.choice(team2.students)
            self.swap_student_between_teams(student_team1, student_team2)
        except ValueError:
            return team_set
        return team_set

    def mutate(self, team_set: PriorityTeamSet) -> List[PriorityTeamSet]:
        """
        Mutate a single teamset into child teamsets
        """
        cloned_team_sets = [team_set.clone() for _ in range(PriorityAlgorithm.MAX_SPREAD)]
        return [self.mutate_team_random(cloned_team_set) for cloned_team_set in cloned_team_sets]

    def swap_student_between_teams(self, student_1: Student, student_2: Student):
        student_1_team = student_1.team
        student_2_team = student_2.team
        student_1.team.remove_student(student_1)
        student_2.team.remove_student(student_2)

        student_1_team.add_student(student_2)
        student_2.add_team(student_1_team)
        student_2_team.add_student(student_1)
        student_1.add_team(student_2_team)
