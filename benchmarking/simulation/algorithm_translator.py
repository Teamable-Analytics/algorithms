from typing import List, Union

from benchmarking.evaluations.goals import DiversityGoal
from models.enums import (
    RequirementOperator,
    Relationship,
    DiversifyType,
    TokenizationConstraintDirection,
)
from models.project import ProjectRequirement
from models.student import Student
from models.team import Team
from models.team_set import TeamSet
from old.team_formation.app.team_generator.algorithm.consts import (
    FRIEND,
    ENEMY,
    DEFAULT,
)
from old.team_formation.app.team_generator.algorithm.priority_algorithm.priority import (
    Priority,
)
from old.team_formation.app.team_generator.student import Student as AlgorithmStudent
from old.team_formation.app.team_generator.team import Team as AlgorithmTeam
from old.team_formation.app.team_generator.team_generator import TeamGenerationOption


class AlgorithmTranslator:
    @staticmethod
    def initial_teams_to_team_generation_options(
        initial_teams: List[Team], num_students: int
    ) -> TeamGenerationOption:
        total_teams = 0
        team_options = []

        for i, initial_team in enumerate(initial_teams):
            team_options.append(
                {
                    "id": initial_team.id,
                    "project_id": initial_team.project_id,
                    "name": initial_team.name
                    or f"Project {initial_team.project_id} - {i}",
                    "requirements": [
                        {
                            "id": requirement.attribute,
                            "operator": AlgorithmTranslator.requirement_operator_to_algorithm_requirement_operator(
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
    def requirement_operator_to_algorithm_requirement_operator(
        requirement: RequirementOperator,
    ) -> str:
        return requirement.value

    @staticmethod
    def algorithm_requirement_operator_to_requirement_operator(
        algorithm_requirement: str,
    ) -> RequirementOperator:
        if algorithm_requirement == "exactly":
            return RequirementOperator.EXACTLY
        if algorithm_requirement == "less than":
            return RequirementOperator.LESS_THAN
        if algorithm_requirement == "more than":
            return RequirementOperator.MORE_THAN

        raise ValueError(
            f"{algorithm_requirement} is not a valid project requirement operator in the algorithms module"
        )

    @staticmethod
    def algorithm_teams_to_team_set(algorithm_teams: List[AlgorithmTeam]) -> TeamSet:
        return TeamSet(
            _id=1,
            teams=[
                AlgorithmTranslator.algorithm_team_to_team(algorithm_team)
                for algorithm_team in algorithm_teams
            ],
        )

    @staticmethod
    def students_to_algorithm_students(
        students: List[Student],
    ) -> List[AlgorithmStudent]:
        return [
            AlgorithmTranslator.student_to_algorithm_student(student)
            for student in students
        ]

    @staticmethod
    def algorithm_students_to_students(
        algorithm_students: List[AlgorithmStudent],
    ) -> List[Student]:
        return [
            AlgorithmTranslator.algorithm_student_to_student(algorithm_student)
            for algorithm_student in algorithm_students
        ]

    @staticmethod
    def team_to_algorithm_team(team: Team) -> AlgorithmTeam:
        students = AlgorithmTranslator.students_to_algorithm_students(team.students)

        return AlgorithmTeam(
            id=str(team.id),
            project_id=team.project_id,
            name=team.name,
            students=students,
            requirements=[
                {
                    "id": req.attribute,
                    "operator": AlgorithmTranslator.requirement_operator_to_algorithm_requirement_operator(
                        req.operator
                    ),
                    "value": req.value,
                }
                for req in team.requirements
            ],
            locked=team.is_locked,
        )

    @staticmethod
    def teams_to_algorithm_teams(teams: List[Team]) -> List[AlgorithmTeam]:
        return [AlgorithmTranslator.team_to_algorithm_team(team) for team in teams]

    @staticmethod
    def algorithm_team_to_team(algorithm_team: AlgorithmTeam) -> Team:
        students = [
            AlgorithmTranslator.algorithm_student_to_student(algorithm_student)
            for algorithm_student in algorithm_team.students
        ]
        team = Team(
            _id=int(algorithm_team.id),
            name=algorithm_team.name,
            project_id=algorithm_team.project_id,
            students=students,
            requirements=[
                ProjectRequirement(
                    attribute=requirement["id"],
                    operator=AlgorithmTranslator.algorithm_requirement_operator_to_requirement_operator(
                        requirement["operator"]
                    ),
                    value=requirement["value"],
                )
                for requirement in algorithm_team.requirements
            ],
            is_locked=algorithm_team.is_locked,
        )

        for student in students:
            student.team = team

        return team

    @staticmethod
    def algorithm_student_to_student(algorithm_student: AlgorithmStudent) -> Student:
        return Student(
            _id=algorithm_student.id,
            attributes=algorithm_student.skills,
            relationships={
                s_id: AlgorithmTranslator.algorithm_relationship_to_relationship(
                    relationship
                )
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
            id=student.id,
            skills=student.attributes,
            relationships={
                student_id: AlgorithmTranslator.relationship_to_algorithm_relationship(
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

    @staticmethod
    def diversity_goal_to_algorithm_priority_dict(
        goal: DiversityGoal,
    ) -> Union[dict, None]:

        priority_type = (
            Priority.TYPE_DIVERSIFY
            if goal.strategy == DiversifyType.DIVERSIFY
            else Priority.TYPE_CONCENTRATE
        )

        limit_option = (
            Priority.MIN_OF
            if goal.tokenization_constraint.direction
            == TokenizationConstraintDirection.MIN_OF
            else Priority.MAX_OF
        )

        # Fixme: work around because priority requires a tokenization constraint currently
        if not goal.tokenization_constraint:
            print("Warning: work around used")
            return {
                "order": goal.importance,
                "constraint": priority_type,
                "skill_id": goal.attribute,
                "limit_option": Priority.MIN_OF,
                "limit": 0,
                "value": -1,
            }

        return {
            "order": goal.importance,
            "constraint": priority_type,
            "skill_id": goal.attribute,
            "limit_option": limit_option,
            "limit": goal.tokenization_constraint.threshold,
            "value": goal.tokenization_constraint.value,
        }
