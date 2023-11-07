import unittest
import copy

from schema import SchemaError

from api.api.validators.generate_teams_validator import GenerateTeamsValidator


class TestGenerateTeamsValidator(unittest.TestCase):
    @classmethod
    def setUp(cls):
        valid_data = {
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
                # TODO: Change this when validate algorithm options
                "algorithm_type": "social",
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

        cls.valid_data = valid_data.copy()

        missing_students_data = valid_data.copy()
        del missing_students_data["students"]
        cls.missing_students_data = missing_students_data

        missing_algorithm_options_data = valid_data.copy()
        del missing_algorithm_options_data["algorithm_options"]
        cls.missing_algorithm_options_data = missing_algorithm_options_data

        missing_team_generation_options_data = valid_data.copy()
        del missing_team_generation_options_data["team_generation_options"]
        cls.missing_team_generation_options_data = missing_team_generation_options_data

        student_with_invalid_relationship_data = copy.deepcopy(valid_data)
        student_with_invalid_relationship_data["students"][0]["relationships"] = {
            "-1": "enemy"
        }
        cls.student_with_invalid_relationship_data = (
            student_with_invalid_relationship_data
        )

        student_with_extra_attribute_data = copy.deepcopy(valid_data)
        student_with_extra_attribute_data["students"][0]["attributes"]["5"] = [1, 2, 3]
        cls.student_with_extra_attribute_data = student_with_extra_attribute_data

        student_with_invalid_project_id_data = copy.deepcopy(valid_data)
        student_with_invalid_project_id_data["students"][0][
            "project_preferences"
        ].append(-1)
        cls.student_with_invalid_project_id_data = student_with_invalid_project_id_data

        team_generation_options_with_duplicate_ids_data = copy.deepcopy(valid_data)
        team_generation_options_with_duplicate_ids_data["team_generation_options"][
            "initial_teams"
        ] += [
            {"id": 3, "project_id": 3},
            {"id": 3, "project_id": 4},
        ]
        cls.team_generation_options_with_duplicate_ids_data = (
            team_generation_options_with_duplicate_ids_data
        )

    def test_valid__happy_json(self):
        try:
            validator = GenerateTeamsValidator(self.valid_data)
            validator.validate()
        except SchemaError as e:
            self.fail("Valid data raised SchemaError unexpectedly")

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
