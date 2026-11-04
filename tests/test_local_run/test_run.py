import copy
import json
import tempfile
import unittest
from pathlib import Path

from local_run.run import DEFAULT_INPUT, LocalRunError, generate_teams, main


def _load_sample_payload():
    with open(DEFAULT_INPUT, encoding="utf-8") as f:
        return json.load(f)


class TestLocalRun(unittest.TestCase):
    def setUp(self):
        self.payload = _load_sample_payload()
        self.student_ids = {s["id"] for s in self.payload["students"]}
        self.team_options = self.payload["team_generation_options"]

    def assert_valid_team_set(self, result):
        teams = result["teams"]["teams"]
        assigned_ids = [s["id"] for team in teams for s in team["students"]]

        self.assertIsNone(result["error"])
        self.assertEqual(len(teams), self.team_options["total_teams"])
        # every student is assigned to exactly one team
        self.assertCountEqual(assigned_ids, self.student_ids)
        for team in teams:
            self.assertGreaterEqual(
                len(team["students"]), self.team_options["min_team_size"]
            )
            self.assertLessEqual(
                len(team["students"]), self.team_options["max_team_size"]
            )

    def test_sample_payload__has_10_to_20_students(self):
        self.assertGreaterEqual(len(self.student_ids), 10)
        self.assertLessEqual(len(self.student_ids), 20)

    def test_generate_teams__sample_payload_creates_valid_teams(self):
        result = generate_teams(self.payload, seed=1)
        self.assert_valid_team_set(result)

    def test_generate_teams__works_for_every_algorithm_type(self):
        for algorithm_type in ["random", "weight", "social", "priority"]:
            with self.subTest(algorithm_type=algorithm_type):
                payload = copy.deepcopy(self.payload)
                if algorithm_type == "random":
                    payload["algorithm_options"] = {"algorithm_type": "random"}
                elif algorithm_type != "priority":
                    payload["algorithm_options"] = {
                        "algorithm_type": algorithm_type,
                        "max_project_preferences": 3,
                        "social_weight": 1,
                        "diversity_weight": 1,
                        "preference_weight": 1,
                        "attributes_to_diversify": [1],
                    }
                self.assert_valid_team_set(generate_teams(payload, seed=1))

    def test_generate_teams__same_seed_gives_same_teams(self):
        first = generate_teams(copy.deepcopy(self.payload), seed=7)
        second = generate_teams(copy.deepcopy(self.payload), seed=7)
        self.assertEqual(first["teams"], second["teams"])

    def test_generate_teams__optional_student_fields_can_be_omitted(self):
        for student in self.payload["students"]:
            del student["relationships"]
            del student["project_preferences"]
        self.payload["algorithm_options"] = {"algorithm_type": "random"}
        self.assert_valid_team_set(generate_teams(self.payload, seed=1))

    def test_generate_teams__raises_if_students_do_not_fit_into_teams(self):
        self.payload["team_generation_options"]["max_team_size"] = 3
        with self.assertRaises(LocalRunError):
            generate_teams(self.payload)

    def test_main__writes_result_to_output_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "result.json"
            exit_code = main(
                ["--input", str(DEFAULT_INPUT), "--output", str(output_path)]
            )

            self.assertEqual(exit_code, 0)
            with open(output_path, encoding="utf-8") as f:
                self.assert_valid_team_set(json.load(f))

    def test_main__returns_error_code_for_missing_input(self):
        self.assertEqual(main(["--input", "does/not/exist.json"]), 1)
