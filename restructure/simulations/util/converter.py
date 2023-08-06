from typing import List

from restructure.models.enums import RequirementType
from restructure.models.project import Project
from restructure.models.student import Student
from restructure.models.team_set import TeamSet
from team_formation.app.team_generator.student import Student as AlgorithmStudent
from team_formation.app.team_generator.team import Team as AlgorithmTeam
from team_formation.app.team_generator.team_generator import TeamGenerationOption


class Converter:
    @staticmethod
    def projects_to_team_generation_option(
        projects: List[Project], num_students: int
    ) -> TeamGenerationOption:
        total_teams = 0
        team_options = []

        counter = 0  # used for team option ids
        for project in projects:
            total_teams += project.num_teams
            for i in range(0, project.num_teams):
                team_options.append(
                    {
                        "id": counter,
                        "project_id": project._id,
                        "name": f"Project {project._id} - {i}",
                        "requirements": [
                            {
                                "id": requirement.attribute,
                                "operator": Converter.requirement_operator_value(requirement.operator),
                                "value": requirement.value,
                            }
                            for requirement in project.requirements
                        ],
                    }
                )
                counter += 1

        min_team_size = num_students // total_teams
        return TeamGenerationOption(
            max_team_size=min_team_size + 1,
            min_team_size=min_team_size,
            total_teams=total_teams,
            team_options=team_options,
        )

    @staticmethod
    def requirement_operator_value(requirement_operator: RequirementType) -> str:
        return requirement_operator.value

    @staticmethod
    def algorithm_output_to_team_set(algorithm_teams: List[AlgorithmTeam]) -> TeamSet:
        # todo: complete
        return TeamSet()

    @staticmethod
    def students_to_algorithm_students(students: List[Student]) -> List[AlgorithmStudent]:
        # todo: complete
        return []