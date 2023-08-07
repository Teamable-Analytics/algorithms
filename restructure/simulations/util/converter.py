from typing import List

from restructure.models.enums import RequirementType, Relationship
from restructure.models.project import ProjectRequirement
from restructure.models.student import Student
from restructure.models.team import Team
from restructure.models.team_set import TeamSet
from team_formation.app.team_generator.algorithm.consts import FRIEND, ENEMY, DEFAULT
from team_formation.app.team_generator.student import Student as AlgorithmStudent
from team_formation.app.team_generator.team import Team as AlgorithmTeam
from team_formation.app.team_generator.team_generator import TeamGenerationOption


class Converter:
    @staticmethod
    def initial_teams_to_team_generation_options(
        initial_teams: List[Team], num_students: int
    ) -> TeamGenerationOption:
        total_teams = 0
        team_options = []

        for i, initial_team in enumerate(initial_teams):
            team_options.append(
                {
                    "id": initial_team._id,
                    "project_id": initial_team.project_id,
                    "name": initial_team.name
                    or f"Project {initial_team.project_id} - {i}",
                    "requirements": [
                        {
                            "id": requirement.attribute,
                            "operator": Converter.requirement_to_algorithm_requirement_operator(
                                requirement.operator
                            ),
                            "value": requirement.value,
                        }
                        for requirement in initial_team.requirements
                    ],
                }
            )

        min_team_size = num_students // total_teams
        return TeamGenerationOption(
            max_team_size=min_team_size + 1,
            min_team_size=min_team_size,
            total_teams=total_teams,
            team_options=team_options,
        )

    @staticmethod
    def requirement_to_algorithm_requirement_operator(
        requirement: RequirementType,
    ) -> str:
        return requirement.value

    @staticmethod
    def algorithm_requirement_operator_to_requirement(
        algorithm_requirement: str,
    ) -> RequirementType:
        """
        TODO: instead of raw strings, ref the dict that stores these in the algo, it's fine since this
            file is the only file that integrates /simulations with /algorithms
        """
        if algorithm_requirement == "exactly":
            return RequirementType.EXACTLY
        if algorithm_requirement == "less than":
            return RequirementType.LESS_THAN
        if algorithm_requirement == "more than":
            return RequirementType.MORE_THAN

        raise ValueError(
            f"{algorithm_requirement} is not a valid project requirement operator in the algorithms module"
        )

    @staticmethod
    def algorithm_teams_to_team_set(algorithm_teams: List[AlgorithmTeam]) -> TeamSet:
        return TeamSet(
            _id=1,
            teams=[
                Converter.algorithm_team_to_team(algorithm_team)
                for algorithm_team in algorithm_teams
            ],
        )

    @staticmethod
    def students_to_algorithm_students(
        students: List[Student],
    ) -> List[AlgorithmStudent]:
        return [Converter.student_to_algorithm_student(student) for student in students]

    @staticmethod
    def algorithm_team_to_team(algorithm_team: AlgorithmTeam) -> Team:
        return Team(
            _id=algorithm_team.id,
            name=algorithm_team.name,
            project_id=algorithm_team.project_id,
            students=[
                Converter.algorithm_student_to_student(algorithm_student)
                for algorithm_student in algorithm_team.students
            ],
            requirements=[
                ProjectRequirement(
                    attribute=requirement["id"],
                    operator=Converter.algorithm_requirement_operator_to_requirement(
                        requirement["operator"]
                    ),
                    value=requirement["value"],
                )
                for requirement in algorithm_team.requirements
            ],
        )

    @staticmethod
    def algorithm_student_to_student(algorithm_student: AlgorithmStudent) -> Student:
        return Student(
            _id=algorithm_student.id,
            attributes=algorithm_student.skills,
            relationships={
                s_id: Converter.algorithm_relationship_to_relationship(relationship)
                for s_id, relationship in algorithm_student.relationships.items()
            },
            preferences=[
                project_id
                for _, project_id in sorted(
                    algorithm_student.preferences.items(), key=lambda item: item[0]
                )
            ],
        )

    @staticmethod
    def student_to_algorithm_student(student: Student) -> AlgorithmStudent:
        return AlgorithmStudent(
            id=student._id,
            skills=student.attributes,
            relationships={
                student_id: Converter.relationship_to_algorithm_relationship(
                    relationship
                )
                for student_id, relationship in student.relationships.items()
            },
            preferences={
                index: project_id
                for index, project_id in enumerate(student.preferences)
            },
        )

    @staticmethod
    def algorithm_relationship_to_relationship(relationship_value: int) -> Relationship:
        if relationship_value == FRIEND:
            return Relationship.FRIEND
        if relationship_value == ENEMY:
            return Relationship.ENEMY

        return Relationship.DEFAULT

    @staticmethod
    def relationship_to_algorithm_relationship(relationship: Relationship) -> int:
        if relationship == Relationship.FRIEND:
            return FRIEND
        if relationship == Relationship.ENEMY:
            return ENEMY

        return DEFAULT
