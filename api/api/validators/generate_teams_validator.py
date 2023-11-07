from typing import List, Optional, Dict

from schema import Schema, SchemaError, Or

from api.api.validators.interface import Validator
from api.models.enums import AlgorithmType, Relationship
from api.models.team import TeamShell


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
                "algorithm_options": Dict,
                "students": List[Dict],
                "team_generation_options": Dict,
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
        # todo: validate that anything that is an id is real (?)
        #   so attributes_to_concentrate is a list of attribute ids, ideally these exist on each student

        # todo: if a max_project_preferences is given, then students can't have more project preferences than that
        pass

    def validate_students(self):
        students: List = self.data.get("students")
        Schema(
            [
                {
                    "id": int,
                    "name": Optional[str],
                    "attributes": {str: List[int]},
                    "relationships": {
                        str: Or(*[relationship.value for relationship in Relationship])
                    },
                    "project_preferences": List[int],
                }
            ]
        ).validate(students)

        student_ids = set()
        for student in students:
            if student.get("_id") in student_ids:
                raise SchemaError("Student ids must be unique.")
            student_ids.add(student.get("_id"))

        teams: List[TeamShell] = self.data.get("team_generation_options").get(
            "initial_teams"
        )

        max_project_preferences = self.data.get("algorithm_options").get(
            "max_project_preferences"
        )
        if max_project_preferences is not None:
            for student in students:
                student_project_preferences = student.get("project_preferences")
                if (
                    student_project_preferences is not None
                    and student_project_preferences > max_project_preferences
                ):
                    raise SchemaError(
                        f"Student {student.id} has {student_project_preferences} project preferences, "
                        + f"but the maximum is {max_project_preferences}."
                    )

        all_projects = set([team.project_id for team in teams])
        for student in students:
            student_project_preferences = student.get("project_preferences")
            if student_project_preferences is None:
                continue

            # Validate if project preferences are unique
            if len(student_project_preferences) != len(
                set(student_project_preferences)
            ):
                raise SchemaError(
                    f"Student {student.id} has duplicate project preferences."
                )

            # Validate if projects under student.project_preferences exist
            if not all_projects.issuperset(student_project_preferences):
                raise SchemaError(
                    f"Student {student.id} has project preferences that do not exist in the project set."
                )

        all_attributes = set()
        for team in teams:
            all_attributes.update(
                [requirement.attribute for requirement in team.requirements]
            )
        for student in students:
            attributes = student.get("attributes")

            # Validate if attribute keys integer string
            try:
                attribute_keys = list(map(int, attributes.keys()))
            except ValueError:
                raise SchemaError("Attribute keys must be integers.")

            # Validate if attribute keys are unique
            if len(attribute_keys) != len(set(attribute_keys)):
                raise SchemaError("Attribute keys must be unique.")

            # Validate if attribute keys exist
            if not all_attributes.issuperset(attribute_keys):
                raise SchemaError(
                    f"Student {student.id} has attributes that do not exist"
                )

    def validate_team_options(self):
        team_options = self.data.get("team_generation_options")
        initial_teams: List[TeamShell] = team_options.get("initial_teams")
        initial_teams_ids = [t.id for t in initial_teams]

        if len(initial_teams_ids) != len(set(initial_teams_ids)):
            raise SchemaError("Team ids must be unique.")
