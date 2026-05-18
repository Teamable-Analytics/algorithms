import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import List

import typer

from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
    PriorityAlgorithmStartType,
    RandomAlgorithmConfig,
    SocialAlgorithmConfig,
    WeightAlgorithmConfig,
)
from algorithms.ai.interfaces.algorithm_options import (
    PriorityAlgorithmOptions,
    RandomAlgorithmOptions,
    SocialAlgorithmOptions,
    WeightAlgorithmOptions,
)
from algorithms.ai.interfaces.team_generation_options import TeamGenerationOptions
from algorithms.dataclasses.enums import AlgorithmType
from algorithms.dataclasses.student import Student
from algorithms.dataclasses.team_set.serializer import TeamSetSerializer

app = typer.Typer()

RUNS_DIR = Path(__file__).parent


def _load_transform(run_dir: Path):
    transform_path = run_dir / "transform.py"
    if not transform_path.exists():
        typer.echo(f"Error: transform.py not found in {run_dir}", err=True)
        raise typer.Exit(1)
    spec = importlib.util.spec_from_file_location("transform", transform_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_options(algorithm_type: AlgorithmType, options_data: dict):
    opts = {"algorithm_type": algorithm_type.value, **options_data}
    if algorithm_type == AlgorithmType.RANDOM:
        return RandomAlgorithmOptions()
    if algorithm_type == AlgorithmType.WEIGHT:
        return WeightAlgorithmOptions.parse_json(opts)
    if algorithm_type == AlgorithmType.PRIORITY:
        return PriorityAlgorithmOptions.parse_json(opts)
    if algorithm_type == AlgorithmType.SOCIAL:
        # SocialAlgorithmOptions has no parse_json; WeightAlgorithmOptions.parse_json
        # returns WeightAlgorithmOptions, so we extract and re-wrap.
        w = WeightAlgorithmOptions.parse_json(opts)
        return SocialAlgorithmOptions(
            max_project_preferences=w.max_project_preferences,
            requirement_weight=w.requirement_weight,
            social_weight=w.social_weight,
            diversity_weight=w.diversity_weight,
            preference_weight=w.preference_weight,
            friend_behaviour=w.friend_behaviour,
            enemy_behaviour=w.enemy_behaviour,
            attributes_to_diversify=w.attributes_to_diversify,
            attributes_to_concentrate=w.attributes_to_concentrate,
        )
    raise ValueError(f"Unknown algorithm type: {algorithm_type}")


def _build_config(algorithm_type: AlgorithmType, config_data: dict):
    if algorithm_type == AlgorithmType.RANDOM:
        return RandomAlgorithmConfig()
    if algorithm_type == AlgorithmType.WEIGHT:
        return WeightAlgorithmConfig()
    if algorithm_type == AlgorithmType.SOCIAL:
        return SocialAlgorithmConfig()
    if algorithm_type == AlgorithmType.PRIORITY:
        kwargs = {k: v for k, v in config_data.items() if k not in ("START_TYPE", "MUTATIONS")}
        if "START_TYPE" in config_data:
            kwargs["START_TYPE"] = PriorityAlgorithmStartType(config_data["START_TYPE"])
        return PriorityAlgorithmConfig(**kwargs)
    raise ValueError(f"Unknown algorithm type: {algorithm_type}")


@app.command()
def run(
    format_name: str = typer.Argument(..., help="Name of the subdirectory under runs/"),
    output: Path = typer.Option(
        None, "--output", "-o", help="Write JSON output to this file (default: stdout)"
    ),
):
    run_dir = RUNS_DIR / format_name
    if not run_dir.is_dir():
        typer.echo(f"Error: runs/{format_name}/ not found", err=True)
        raise typer.Exit(1)

    for required in ("input.csv", "params.json", "transform.py"):
        if not (run_dir / required).exists():
            typer.echo(f"Error: {required} not found in runs/{format_name}/", err=True)
            raise typer.Exit(1)

    transform = _load_transform(run_dir)
    students: List[Student] = transform.get_students(str(run_dir / "input.csv"))

    with open(run_dir / "params.json") as f:
        params = json.load(f)

    algorithm_type = AlgorithmType(params["algorithm_type"])

    tg = params["team_generation"]
    max_team_size = tg["max_team_size"]
    min_team_size = tg["min_team_size"]
    total_teams = tg.get("total_teams", "auto")
    if total_teams == "auto":
        total_teams = math.ceil(len(students) / max_team_size)

    team_generation_options = TeamGenerationOptions(
        max_team_size=max_team_size,
        min_team_size=min_team_size,
        total_teams=total_teams,
        initial_teams=[],
    )

    algorithm_options = _build_options(algorithm_type, params.get("algorithm_options", {}))

    algorithm_config = None
    if "algorithm_config" in params:
        algorithm_config = _build_config(algorithm_type, params["algorithm_config"])

    runner = AlgorithmRunner(
        algorithm_type=algorithm_type,
        team_generation_options=team_generation_options,
        algorithm_options=algorithm_options,
        algorithm_config=algorithm_config,
    )

    team_set = runner.generate(students)

    output_dict = TeamSetSerializer().default(team_set)

    unassigned = [s for s in students if not s.team]
    if unassigned:
        from algorithms.dataclasses.student.serializer import StudentSerializer
        serializer = StudentSerializer()
        output_dict["unassigned"] = [serializer.default(s) for s in unassigned]

    result = json.dumps(output_dict, indent=2)

    if output:
        output.write_text(result)
        typer.echo(f"Teams written to {output}", err=True)
    else:
        print(result)


if __name__ == "__main__":
    app()
