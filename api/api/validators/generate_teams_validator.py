from schema import Schema, SchemaError

from api.ai.algorithm_runner import AlgorithmRunner
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.api.validators.interface import Validator
from api.models.enums import AlgorithmType
from api.models.student import Student
from api.api.utils.relationship import get_relationship


class GenerateTeamsValidator(Validator):
    def validate(self):
        self._validate_schema()
        self.validate_algorithm_type()
        self.validate_team_options()
        self.validate_algorithm_options()
        self.validate_algorithm_configs()
        self.validate_students()

    def _validate_schema(self):
        Schema(dict).validate(self.data)
        Schema(list).validate(self.data.get("students"))
        Schema(dict).validate(self.data.get("algorithm_options"))
        Schema(dict).validate(self.data.get("team_generation_options"))

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
        algorithm_option = dict.copy(self.data.get("algorithm_options"))
        algorithm_type = AlgorithmType(algorithm_option.pop("algorithm_type"))
        algorithm_option_cls = AlgorithmRunner.get_algorithm_option_class(
            algorithm_type
        )

        algorithm_option_cls(**algorithm_option).validate()

    def validate_algorithm_configs(self):
        algorithm_type = AlgorithmType(self.data.get("algorithm_options").get("algorithm_type"))
        algorithm_config = self.data.get("algorithm_config")
        algorithm_config_cls = AlgorithmRunner.get_algorithm_config_class(algorithm_type)

        algorithm_config_cls(**algorithm_config).validate()

    def validate_students(self):
        students = self.data.get("students")
        for student in students:
            relationships = {
                student_id: get_relationship(relationship)
                for student_id, relationship in student.get("relationships").items()
            }
            Student(
                _id=student.get("id"),
                name=student.get("name"),
                relationships=relationships,
                attributes=student.get("attributes"),
                project_preferences=student.get("project_preferences"),
            ).validate()

    def validate_team_options(self):
        TeamGenerationOptions(**self.data.get("team_generation_options")).validate()
