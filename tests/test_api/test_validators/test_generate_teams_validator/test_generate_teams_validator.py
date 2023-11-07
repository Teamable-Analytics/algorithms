import unittest
import copy

from schema import SchemaError

from api.api.validators.generate_teams_validator import GenerateTeamsValidator


class TestGenerateTeamsValidator(unittest.TestCase):
    @classmethod
    def setUp(cls):
        valid_random_algorithm_data = {
            "students": [
                {
                    "id": 1,
                    "attributes": {
                        "1": [1, 2],
                        "2": [0, 1, 2, 3, 4],
                        "3": [24, 42],
                        "4": [1],
                    },
                    "relationships": {
                        "2": "friend",
                        "3": "default",
                        "4": "enemy",
                    },
                    "project_preferences": [1, 2],
                },
                {
                    "id": 2,
                    "attributes": {
                        "1": [2],
                        "2": [2, 3],
                        "3": [2],
                        "4": [1, 12],
                    },
                    "relationships": {
                        "1": "friend",
                        "3": "default",
                        "4": "enemy",
                    },
                    "project_preferences": [1, 2],
                },
                {
                    "id": 3,
                    "attributes": {
                        "1": [7],
                        "2": [0, 5, 23],
                        "3": [22],
                        "4": [0, 1, 2, 3, 4],
                    },
                    "relationships": {
                        "1": "default",
                        "2": "default",
                        "4": "friend",
                    },
                    "project_preferences": [2, 1],
                },
                {
                    "id": 4,
                    "attributes": {
                        "1": [2, 17],
                        "2": [12],
                        "3": [3, 4, 5, 6],
                        "4": [0],
                    },
                    "relationships": {
                        "1": "default",
                        "2": "default",
                        "3": "friend",
                    },
                    "project_preferences": [2, 1],
                },
            ],
            "algorithm_options": {
                "algorithm_type": "random",
            },
            "team_generation_options": {
                "initial_teams": [
                    {
                        "id": 1,
                        "project_id": 1,
                        "requirements": [
                            {
                                "attribute": 1,
                                "operator": "exactly",
                                "value": 2,
                            },
                            {
                                "attribute": 2,
                                "operator": "less than",
                                "value": 4,
                            },
                            {
                                "attribute": 3,
                                "operator": "more than",
                                "value": 0,
                            },
                            {
                                "attribute": 4,
                                "operator": "more than",
                                "value": 0,
                            },
                        ],
                    },
                    {
                        "id": 2,
                        "project_id": 2,
                    },
                ],
                "total_teams": 2,
                "max_team_size": 2,
                "min_team_size": 1,
            },
        }

        valid_social_algorithm_data = copy.deepcopy(valid_random_algorithm_data)
        cls.valid_random_algorithm_data = valid_random_algorithm_data.copy()

        valid_weight_algorithm_data = copy.deepcopy(valid_random_algorithm_data)
        valid_weight_algorithm_data["algorithm_options"] = {
            "algorithm_type": "weight",
            "max_project_preferences": 3,
        }
        cls.valid_weight_algorithm_data = valid_weight_algorithm_data

        valid_social_algorithm_data["algorithm_options"] = {
            "algorithm_type": "social",
            "max_project_preferences": 3,
        }
        cls.valid_social_algorithm_data = valid_social_algorithm_data

        valid_priority_algorithm_data = copy.deepcopy(valid_random_algorithm_data)
        valid_priority_algorithm_data["algorithm_options"] = {
            "algorithm_type": "priority_new",
            "max_project_preferences": 3,
            "priorities": [],
        }
        cls.valid_priority_algorithm_data = valid_priority_algorithm_data

        missing_students_data = valid_random_algorithm_data.copy()
        del missing_students_data["students"]
        cls.missing_students_data = missing_students_data

        missing_algorithm_options_data = valid_random_algorithm_data.copy()
        del missing_algorithm_options_data["algorithm_options"]
        cls.missing_algorithm_options_data = missing_algorithm_options_data

        missing_team_generation_options_data = valid_random_algorithm_data.copy()
        del missing_team_generation_options_data["team_generation_options"]
        cls.missing_team_generation_options_data = missing_team_generation_options_data

        student_with_invalid_relationship_data = copy.deepcopy(
            valid_random_algorithm_data
        )
        student_with_invalid_relationship_data["students"][0]["relationships"] = {
            "-1": "enemy"
        }
        cls.student_with_invalid_relationship_data = (
            student_with_invalid_relationship_data
        )

        student_with_extra_attribute_data = copy.deepcopy(valid_random_algorithm_data)
        student_with_extra_attribute_data["students"][0]["attributes"]["5"] = [1, 2, 3]
        cls.student_with_extra_attribute_data = student_with_extra_attribute_data

        student_with_invalid_project_id_data = copy.deepcopy(
            valid_random_algorithm_data
        )
        student_with_invalid_project_id_data["students"][0][
            "project_preferences"
        ].append(-1)
        cls.student_with_invalid_project_id_data = student_with_invalid_project_id_data

        team_generation_options_with_duplicate_ids_data = copy.deepcopy(
            valid_random_algorithm_data
        )
        team_generation_options_with_duplicate_ids_data["team_generation_options"][
            "initial_teams"
        ] += [
            {"id": 3, "project_id": 3},
            {"id": 3, "project_id": 4},
        ]
        cls.team_generation_options_with_duplicate_ids_data = (
            team_generation_options_with_duplicate_ids_data
        )

    def test_valid__random_algorithm(self):
        try:
            validator = GenerateTeamsValidator(self.valid_random_algorithm_data)
            validator.validate()
        except SchemaError:
            self.fail("Valid data for Random Algorithm raised SchemaError unexpectedly")

    def test_valid__weight_algorithm(self):
        try:
            validator = GenerateTeamsValidator(self.valid_weight_algorithm_data)
            validator.validate()
        except SchemaError:
            self.fail("Valid data for Weight Algorithm raised SchemaError unexpectedly")

    def test_valid__social_algorithm(self):
        try:
            validator = GenerateTeamsValidator(self.valid_social_algorithm_data)
            validator.validate()
        except SchemaError:
            self.fail("Valid data for Social Algorithm raised SchemaError unexpectedly")

    def test_valid__priority_algorithm(self):
        try:
            validator = GenerateTeamsValidator(self.valid_priority_algorithm_data)
            validator.validate()
        except SchemaError:
            self.fail(
                "Valid data for Priority Algorithm raised SchemaError unexpectedly"
            )

    def test_errors__top_levels(self):
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(self.missing_students_data)
            validator.validate()
        self.assertEqual(e.exception.code, "Missing key: 'students'")

        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(self.missing_algorithm_options_data)
            validator.validate()
        self.assertEqual(e.exception.code, "Missing key: 'algorithm_options'")

        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(
                self.missing_team_generation_options_data
            )
            validator.validate()
        self.assertEqual(e.exception.code, "Missing key: 'team_generation_options'")

    def test_errors__students(self):
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(
                self.student_with_invalid_relationship_data
            )
            validator.validate()
        self.assertEqual(
            e.exception.code, "Student 1 has relationships with unknown students."
        )

        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(self.student_with_extra_attribute_data)
            validator.validate()
        self.assertEqual(
            e.exception.code, "Student 1 has attributes that do not exist."
        )

        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(
                self.student_with_invalid_project_id_data
            )
            validator.validate()
        self.assertEqual(
            e.exception.code,
            "Student 1 has project preferences that do not exist in the project set.",
        )

    def test_errors__team_generation_options(self):
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(
                self.team_generation_options_with_duplicate_ids_data
            )
            validator.validate()
        self.assertEqual(e.exception.code, "Team ids must be unique.")

    def test_errors__algorithm_options__random_algorithm(self):
        invalid_field_random_algorithm_data = copy.deepcopy(
            self.valid_random_algorithm_data
        )
        invalid_field_random_algorithm_data["algorithm_options"][
            "max_project_preferences"
        ] = 3
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(invalid_field_random_algorithm_data)
            validator.validate()
        self.assertIn("Wrong key 'max_project_preferences' in ", e.exception.code)

    def test_errors__algorithm_options__weight_algorithm(self):
        invalid_field_weight_algorithm_data = copy.deepcopy(
            self.valid_weight_algorithm_data
        )
        invalid_field_weight_algorithm_data["algorithm_options"]["priority"] = []
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(invalid_field_weight_algorithm_data)
            validator.validate()
        self.assertIn("Wrong key 'priority' in ", e.exception.code)

    def test_errors__algorithm_options__social_algorithm(self):
        invalid_field_social_algorithm_data = copy.deepcopy(
            self.valid_social_algorithm_data
        )
        invalid_field_social_algorithm_data["algorithm_options"]["priority"] = []
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(invalid_field_social_algorithm_data)
            validator.validate()
        self.assertIn("Wrong key 'priority' in ", e.exception.code)

    def test_errors__algorithm_options__priority_algorithm(self):
        invalid_field_priority_algorithm_data = copy.deepcopy(
            self.valid_priority_algorithm_data
        )
        invalid_field_priority_algorithm_data["algorithm_options"]["random_field"] = []
        with self.assertRaises(SchemaError) as e:
            validator = GenerateTeamsValidator(invalid_field_priority_algorithm_data)
            validator.validate()
        self.assertIn("Wrong key 'random_field' in ", e.exception.code)
