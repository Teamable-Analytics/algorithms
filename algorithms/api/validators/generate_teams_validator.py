from typing import List, Dict

from schema import Schema, SchemaError, Or, Optional

from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.api.validators.interface import Validator
from algorithms.utils.relationship import get_relationship_str
from algorithms.dataclasses.enums import (
    AlgorithmType,
    Relationship,
    RequirementOperator,
)


class GenerateTeamsValidator(Validator):
    """
    Validates that data passed can be used together with other data.

    NOTE: Semantically, validations that can be performed solely with the data of a single
            dataclasses are placed within that dataclasses, but validations that require
            outside context or compatability with other objects are placed here.
    """

    def validate(self):
        self._validate_schema()

        self.validate_algorithm_type()
        self.validate_team_options()
        self.validate_algorithm_options()
        self.validate_students()

    def _validate_schema(self):
        Schema(
            {
                "algorithm_options": dict,
                "students": [dict],
                "team_generation_options": dict,
            }
        ).validate(self.data)

    def validate_algorithm_type(self):
        algorithm_type = self.data.get("algorithm_options").get("algorithm_type")
        Schema(str).validate(algorithm_type)
        try:
            AlgorithmType(algorithm_type)
        except ValueError:
            raise SchemaError(
                f"Algorithm type {algorithm_type} is not a valid algorithm type."
            )

    def validate_algorithm_options(self):
        algorithm_options = self.data.get("algorithm_options")

        # Validate schema
        algorithm_options_cls = AlgorithmRunner.get_algorithm_option_class(
            AlgorithmType(algorithm_options.get("algorithm_type"))
        )
        algorithm_options_schema = algorithm_options_cls.get_schema()
        algorithm_options_schema.validate(algorithm_options)

    def _validate_student_ids_unique(self, students: List[Dict]):
        student_ids = set()
        for student in students:
            student_id = student.get("id")
            if student_id in student_ids:
                raise SchemaError(
                    f"Student ids must be unique. Student {student_id} is duplicated."
                )
            student_ids.add(student_id)

    def _validate_student_project_preferences_exist(
        self, students: List[Dict], teams: List[Dict]
    ):
        all_projects = set([team.get("project_id") for team in teams])
        for student in students:
            student_project_preferences = student.get("project_preferences")
            if student_project_preferences is None:
                continue

            # Validate if projects under student.project_preferences exist
            if not all_projects.issuperset(student_project_preferences):
                raise SchemaError(
                    f"Student {student.get('id')} has project preferences that do not exist in the project set."
                )

    def _validate_student_project_preferences(
        self, students: List[Dict], max_project_preferences: int
    ):
        for student in students:
            student_project_preferences = student.get("project_preferences")
            if (
                student_project_preferences is not None
                and len(student_project_preferences) > max_project_preferences
            ):
                raise SchemaError(
                    f"Student {student.get('id')} has {student_project_preferences} project preferences, "
                    + f"but the maximum is {max_project_preferences}."
                )

    def _validate_student_attributes(self, students: List[Dict], teams: List[Dict]):
        all_attributes = set()
        for team in teams:
            all_attributes.update(
                [
                    requirement.get("attribute")
                    for requirement in team.get("requirements")
                ]
                if team.get("requirements")
                else []
            )
        for student in students:
            attributes = student.get("attributes")
            if attributes is None:
                raise SchemaError(f"Student {student.get('id')} has no attributes.")

            # Validate if attribute keys integer string
            try:
                attribute_keys = list(map(int, attributes.keys())) if attributes else []
            except ValueError:
                raise SchemaError("Attribute keys must be integers.")

            # Validate if attribute keys are unique
            if len(attribute_keys) != len(set(attribute_keys)):
                raise SchemaError("Attribute keys must be unique.")

            # Validate if attribute keys exist
            if not all_attributes.issuperset(attribute_keys):
                raise SchemaError(
                    f"Student {student.get('id')} has attributes that do not exist."
                )

    def _validate_student_relationships(self, students: List[Dict]):
        student_ids = set([student.get("id") for student in students])

        for student in students:
            relationships = student.get("relationships")

            # Validate if relationship keys integer string
            try:
                relationship_keys = list(map(int, relationships.keys()))
            except ValueError:
                raise SchemaError("Relationship keys must be integers.")

            # Validate if relationship keys are unique
            if len(relationship_keys) != len(set(relationship_keys)):
                raise SchemaError("Relationship keys must be unique.")

            # Validate if relationship keys exist
            if not student_ids.issuperset(relationship_keys):
                raise SchemaError(
                    f"Student {student.get('id')} has relationships with unknown students."
                )

    def _validate_student_ids_unique(self, students: List[Dict]):
        student_ids = set()
        for student in students:
            student_id = student.get("id")
            if student_id in student_ids:
                raise SchemaError(
                    f"Student ids must be unique. Student {student_id} is duplicated."
                )
            student_ids.add(student_id)

    def _validate_student_project_preferences_exist(
        self, students: List[Dict], teams: List[Dict]
    ):
        all_projects = set([team.get("project_id") for team in teams])
        for student in students:
            student_project_preferences = student.get("project_preferences")
            if student_project_preferences is None:
                continue

            # Validate if projects under student.project_preferences exist
            if not all_projects.issuperset(student_project_preferences):
                raise SchemaError(
                    f"Student {student.get('id')} has project preferences that do not exist in the project set."
                )

    def _validate_student_project_preferences(
        self, students: List[Dict], max_project_preferences: int
    ):
        for student in students:
            student_project_preferences = student.get("project_preferences")
            if (
                student_project_preferences is not None
                and len(student_project_preferences) > max_project_preferences
            ):
                raise SchemaError(
                    f"Student {student.get('id')} has {student_project_preferences} project preferences, "
                    + f"but the maximum is {max_project_preferences}."
                )

    def _validate_student_attributes(self, students: List[Dict], teams: List[Dict]):
        all_attributes = set()
        for team in teams:
            all_attributes.update(
                [
                    requirement.get("attribute")
                    for requirement in team.get("requirements")
                ]
                if team.get("requirements")
                else []
            )
        for student in students:
            attributes = student.get("attributes")
            if attributes is None:
                raise SchemaError(f"Student {student.get('id')} has no attributes.")

            # Validate if attribute keys integer string
            Schema(Or({str: list}, {})).validate(attributes)

    def _validate_student_relationships(self, students: List[Dict]):
        student_ids = set([student.get("id") for student in students])

        for student in students:
            relationships = student.get("relationships")

            # Validate if relationship keys integer string
            try:
                relationship_keys = list(map(int, relationships.keys()))
            except ValueError:
                raise SchemaError("Relationship keys must be integers.")

            # Validate if relationship keys exist
            if not student_ids.issuperset(relationship_keys):
                raise SchemaError(
                    f"Student {student.get('id')} has relationships with unknown students."
                )

    def validate_students(self):
        students: List = self.data.get("students")
        Schema(
            [
                {
                    "id": int,
                    "attributes": Or({str: [int]}, {}),
                    Optional("name"): str,
                    Optional("relationships"): Or(
                        {
                            str: Or(
                                *[
                                    get_relationship_str(relationship)
                                    for relationship in Relationship
                                ]
                            )
                        },
                        {},
                    ),
                    Optional("project_preferences"): [int],
                }
            ]
        ).validate(students)

        self._validate_student_ids_unique(students)

        max_project_preferences = self.data.get("algorithm_options").get(
            "max_project_preferences"
        )
        if max_project_preferences is not None:
            self._validate_student_project_preferences(
                students, max_project_preferences
            )

        teams = self.data.get("team_generation_options").get("initial_teams")
        self._validate_student_project_preferences_exist(students, teams)

        self._validate_student_attributes(students, teams)

        self._validate_student_relationships(students)

    def validate_team_options(self):
        team_options = self.data.get("team_generation_options")

        Schema(
            {
                "initial_teams": [
                    {
                        "id": int,
                        Optional("name"): Or(str, None),
                        Optional("project_id"): Or(int, None),
                        Optional("requirements"): [
                            {
                                "attribute": int,
                                "operator": Or(
                                    *[op.value for op in RequirementOperator]
                                ),
                                "value": int,
                            }
                        ],
                        Optional("is_locked"): bool,
                    }
                ],
                "max_team_size": int,
                "min_team_size": int,
                "total_teams": int,
            }
        ).validate(team_options)

        initial_teams = team_options.get("initial_teams")
        initial_teams_ids = [t.get("id") for t in initial_teams]

        if len(initial_teams_ids) != len(set(initial_teams_ids)):
            raise SchemaError("Team ids must be unique.")
