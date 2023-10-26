from schema import Schema, SchemaError

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.api.validators.interface import Validator
from api.models.enums import AlgorithmType
from api.models.student import Student
from api.api.utils.relationship import get_relationship


class GenerateTeamsValidator(Validator):
    """
    Validates that data passed can be used together with other data.

    NOTE: Semantically, validations that can be performed solely with the data of a single
            dataclasses are placed within that dataclasses, but validations that require
            outside context or compatability with other objects are placed here.
    """
    def validate(self):
        self._validate_schema()

        # todo: remember, each of these functions should use Schema to validate the shape of the data
        self.validate_algorithm_type()
        self.validate_team_options()
        self.validate_algorithm_options()
        self.validate_algorithm_configs()
        self.validate_students()

    def _validate_schema(self):
        # todo: should actually validate schemas entirely, beyond just being a dict, which
        #   keys and what are their types and nested object types
        Schema(dict).validate(self.data)

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

    def validate_algorithm_configs(self):
        pass

    def validate_students(self):
        # todo: validate student ids are unique
        # todo: validate that if project preferences are specified, then the project ids exist in the team options

        # used to validate a Student dataclass object
        # Schema(int).validate(self.id)
        # if self.name:
        #     Schema(str).validate(self.name)
        # Schema(dict).validate(self.relationships)
        # for student_id, relationship in self.relationships.items():
        #     Schema(str).validate(student_id)
        #     Schema(Relationship).validate(relationship)
        # Schema(dict).validate(self.attributes)
        # Schema(list).validate(self.project_preferences)

        # will be converted to look more like:
        # Schema([
        #     {
        #         "_id": int,
        #
        #     }
        # ]).validate(self.data)

        pass

    def validate_team_options(self):
        # todo: validate team shell ids are unique, if given
        # todo: team shells with the same project_id should have the same requirements (?)
        pass
