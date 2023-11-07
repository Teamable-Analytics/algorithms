import unittest


class TestGenerateTeamsValidator(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.valid_data = {
            "students": [
                {
                    "id": 1,
                    "attribute": {
                        "1": [1, 2],
                        "2": [0, 1, 2, 3, 4],
                        "3": [24, 42],
                        "4": [1],
                    },
                    "relationship": {
                        "2": "friend",
                        "3": "default",
                        "4": "enemy",
                    },
                    "project_preferences": [1, 2],
                },
                {
                    "id": 2,
                    "attribute": {
                        "1": [2],
                        "2": [2, 3],
                        "3": [2],
                        "4": [1, 12],
                    },
                    "relationship": {
                        "1": "friend",
                        "3": "default",
                        "4": "enemy",
                    },
                    "project_preferences": [1, 2],
                },
                {
                    "id": 3,
                    "attribute": {
                        "1": [7],
                        "2": [0, 5, 23],
                        "3": [22],
                        "4": [0, 1, 2, 3, 4],
                    },
                    "relationship": {
                        "1": "default",
                        "2": "default",
                        "4": "friend",
                    },
                    "project_preferences": [2, 1],
                },
                {
                    "id": 4,
                    "attribute": {
                        "1": [2, 17],
                        "2": [12],
                        "3": [3, 4, 5, 6],
                        "4": [0],
                    },
                    "relationship": {
                        "1": "default",
                        "2": "default",
                        "3": "friend",
                    },
                    "project_preferences": [2, 1],
                }
            ],
            "algorithm_options": {
                # TODO: Change this when validate algorithm options
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
                    }
                ],
                "team_size": 2,
                "max_team_size": 2,
                "min_team_size": 1,
            },
        }
