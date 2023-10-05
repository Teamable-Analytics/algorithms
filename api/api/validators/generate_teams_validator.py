from api.validators.interface import Validator


class GenerateTeamsValidator(Validator):
    def validate(self):
        self._validate_schema()
        self.validate_algorithm_type()
        self.validate_team_options()
        self.validate_algorithm_options()
        self.validate_projects()
        self.validate_students()

    def _validate_schema(self):
        pass

    def validate_algorithm_type(self):
        pass

    def validate_algorithm_options(self):
        pass

    def validate_projects(self):
        pass

    def validate_students(self):
        pass

    def validate_team_options(self):
        pass

