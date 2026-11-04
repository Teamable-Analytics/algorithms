"""
Runs the team generation locally, without Canvas, Django or a database.

The input is the same JSON payload the API accepts at POST /api/generate/teams, and the
output has the same shape as the API response. Technical settings (file paths, seed,
priority algorithm limits) come from environment variables, see env/local_run.env.example.
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from schema import SchemaError

from algorithms import api
from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from algorithms.api.utils.generate_teams_data_loader import GenerateTeamsDataLoader
from algorithms.api.validators.generate_teams_validator import GenerateTeamsValidator
from algorithms.dataclasses.enums import AlgorithmType
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team_set import TeamSet
from algorithms.dataclasses.team_set.serializer import TeamSetSerializer

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / "env" / "local_run.env"
DEFAULT_INPUT = (
    Path(__file__).resolve().parent
    / "sample_data"
    / "payload_priority_15_students.json"
)

# environment variable -> field of PriorityAlgorithmConfig
PRIORITY_CONFIG_ENV_VARS = {
    "TEAMGEN_PRIORITY_MAX_TIME": "MAX_TIME",
    "TEAMGEN_PRIORITY_MAX_ITERATE": "MAX_ITERATE",
    "TEAMGEN_PRIORITY_MAX_KEEP": "MAX_KEEP",
    "TEAMGEN_PRIORITY_MAX_SPREAD": "MAX_SPREAD",
}


class LocalRunError(Exception):
    pass


def _get_int_env(name: str) -> Optional[int]:
    value = os.environ.get(name, "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        raise LocalRunError(
            f"Environment variable {name} must be an integer, got '{value}'."
        )


def build_priority_config() -> Optional[PriorityAlgorithmConfig]:
    """
    Returns a PriorityAlgorithmConfig from the TEAMGEN_PRIORITY_* variables, or None to use the defaults.
    """
    overrides = {
        field: _get_int_env(env_var)
        for env_var, field in PRIORITY_CONFIG_ENV_VARS.items()
    }
    overrides = {k: v for k, v in overrides.items() if v is not None}
    if not overrides:
        return None
    return PriorityAlgorithmConfig(**overrides)


def generate_teams(
    payload: Dict[str, Any], seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validates the payload, runs the algorithm and returns the response like the API does.

    Raises LocalRunError if the payload is invalid or not every student could be assigned to a team.
    """
    if seed is not None:
        random.seed(seed)

    try:
        GenerateTeamsValidator(payload).validate()
    except SchemaError as e:
        raise LocalRunError(f"Invalid payload: {e}")
    input_data = GenerateTeamsDataLoader(payload).load()

    algorithm_config = None
    if input_data.algorithm_type == AlgorithmType.PRIORITY:
        algorithm_config = build_priority_config()

    runner = AlgorithmRunner(
        algorithm_type=input_data.algorithm_type,
        team_generation_options=input_data.team_generation_options,
        algorithm_options=input_data.algorithm_options,
        algorithm_config=algorithm_config,
    )
    team_set = runner.generate(input_data.students)

    unassigned = _get_unassigned_student_ids(input_data.students, team_set)
    if unassigned:
        raise LocalRunError(f"Students {unassigned} were not assigned to any team.")

    return {
        "teams": TeamSetSerializer().default(team_set),
        "metadata": {"version": api.VERSION, "timestamp": time.time()},
        "error": None,
    }


def _get_unassigned_student_ids(
    students: List[Student], team_set: TeamSet
) -> List[int]:
    assigned = {s.id for team in team_set.teams for s in team.students}
    return [s.id for s in students if s.id not in assigned]


def format_summary(result: Dict[str, Any]) -> str:
    lines = []
    for team in result["teams"]["teams"]:
        names = ", ".join(s["name"] or str(s["id"]) for s in team["students"])
        lines.append(
            f"{team['name'] or team['id']} ({len(team['students'])} students): {names}"
        )
    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m local_run",
        description="Generate teams locally from a JSON payload (no Canvas, no database).",
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Path to the payload JSON (env: TEAMGEN_INPUT, default: sample payload)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Write the result JSON to this file (env: TEAMGEN_OUTPUT, default: stdout)",
    )
    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        help="Random seed for reproducible results (env: TEAMGEN_SEED)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    # values that are already set in the environment take precedence over the env file
    load_dotenv(ENV_FILE)
    args = parse_args(argv)

    try:
        input_path = Path(
            args.input or os.environ.get("TEAMGEN_INPUT") or DEFAULT_INPUT
        )
        output_path = args.output or os.environ.get("TEAMGEN_OUTPUT")
        seed = args.seed if args.seed is not None else _get_int_env("TEAMGEN_SEED")

        if not input_path.is_absolute():
            input_path = ROOT_DIR / input_path
        if not input_path.exists():
            raise LocalRunError(f"Input file {input_path} not found.")
        with open(input_path, encoding="utf-8") as f:
            payload = json.load(f)

        print(f"Generating teams from {input_path}", file=sys.stderr)
        result = generate_teams(payload, seed=seed)
    except LocalRunError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(format_summary(result), file=sys.stderr)
    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    if output_path:
        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = ROOT_DIR / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result_json + "\n", encoding="utf-8")
        print(f"Teams written to {output_path}", file=sys.stderr)
    else:
        print(result_json)
    return 0
