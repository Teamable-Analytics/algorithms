from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, TYPE_CHECKING

from api.ai.interfaces.algorithm_options import AlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet

if TYPE_CHECKING:
    from api.ai.interfaces.algorithm_config import AlgorithmConfig


class Algorithm(ABC):
    def __init__(
        self,
        algorithm_options: AlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        algorithm_config: "AlgorithmConfig" = None,
    ):
        self.algorithm_options: AlgorithmOptions = algorithm_options
        self.team_generation_options: TeamGenerationOptions = team_generation_options
        self.algorithm_config: "AlgorithmConfig" = algorithm_config
        self.teams: List[Team] = Algorithm.create_initial_teams(
            self.team_generation_options
        )

    @abstractmethod
    def generate(self, students: List[Student]) -> TeamSet:
        raise NotImplementedError

    def get_remaining_students(self, students: List[Student]) -> List[Student]:
        return [student for student in students if not student.team]

    def get_available_teams(
        self, all_teams: List[Team], student: Student = None
    ) -> List[Team]:
        available_teams = []
        for team in all_teams:
            if (
                team.size < self.team_generation_options.max_team_size
                and not team.is_locked
            ):
                if not student:
                    available_teams.append(team)
                elif student and self.student_permitted_in_team(student, team):
                    available_teams.append(team)

        return available_teams

    def student_permitted_in_team(self, student: Student, team: Team) -> bool:
        """Can be overridden in Algorithms to support custom rules for whether a student can be added to a team"""
        return True

    @staticmethod
    def create_initial_teams(
        team_generation_options: TeamGenerationOptions,
    ) -> List[Team]:
        initial_teams: List[Team] = []
        if team_generation_options.initial_teams:
            initial_teams.extend(
                [
                    Team.from_shell(shell)
                    for shell in team_generation_options.initial_teams
                ]
            )

        largest_existing_id = max([t.id for t in initial_teams]) if initial_teams else 0
        team_names = set([t.name for t in initial_teams])

        # Create the remaining teams with unique names
        new_team_id = largest_existing_id + 1
        while len(initial_teams) < team_generation_options.total_teams:
            name = f"Team {new_team_id}"
            if name not in team_names:
                new_team = Team(_id=new_team_id, name=name)
                initial_teams.append(new_team)
                team_names.add(new_team.name)
            new_team_id += 1

        return initial_teams


class ChooseAlgorithm(Algorithm):
    @abstractmethod
    def choose(
        self, teams: List[Team], students: List[Student]
    ) -> Tuple[Optional[Team], Optional[Student]]:
        raise NotImplementedError
