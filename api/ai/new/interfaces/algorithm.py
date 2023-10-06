from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from api.ai.new.interfaces.algorithm_config import AlgorithmConfig
from api.ai.new.interfaces.algorithm_options import AlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class Algorithm(ABC):
    def __init__(
        self,
        algorithm_options: AlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
            algorithm_config: AlgorithmConfig = None,
    ):
        self.algorithm_options: AlgorithmOptions = algorithm_options
        self.team_generation_options: TeamGenerationOptions = team_generation_options
        self.algorithm_config: AlgorithmConfig = algorithm_config
        self.teams: List[Team] = []

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


class ChooseAlgorithm(Algorithm):
    @abstractmethod
    def choose(
        self, teams: List[Team], students: List[Student]
    ) -> Tuple[Optional[Team], Optional[Student]]:
        raise NotImplementedError
