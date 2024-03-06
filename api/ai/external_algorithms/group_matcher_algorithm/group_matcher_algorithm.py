import csv
from itertools import cycle
import os
import time
from pathlib import Path
from typing import List, Dict

import pandas as pd

from api.ai.external_algorithms.group_matcher_algorithm.custom_modes import GroupMatcherStudent
from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_config import GroupMatcherAlgorithmConfig
from api.ai.interfaces.algorithm_options import GroupMatcherAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class GroupMatcherAlgorithm(Algorithm):
    student_trace: Dict[int, Student]
    team_trace: Dict[int, Team]
    team_cycler: cycle[Team]

    group_matcher_input_data_file_path: Path
    group_matcher_output_data_file_path: Path
    group_matcher_config_path: Path

    def __init__(
            self,
            algorithm_options: GroupMatcherAlgorithmOptions,
            team_generation_options: TeamGenerationOptions,
            algorithm_config: GroupMatcherAlgorithmConfig,
    ):
        super().__init__(algorithm_options, team_generation_options, algorithm_config)
        self.group_matcher_input_data_file_path = Path(algorithm_config.csv_input_path)
        self.group_matcher_run_path = algorithm_config.group_matcher_run_path

        self.prepare_file_environment()

        self.team_trace = {team_idx + 1: team for team_idx, team in enumerate(self.teams)}
        self.team_cycler = cycle(self.teams)

    def prepare_file_environment(self):
        class_size = int(self.group_matcher_input_data_file_path.stem.split("-")[0])
        self.group_matcher_run_path = self.group_matcher_run_path
        self.group_matcher_output_data_file_path = Path.cwd() / f"out-private-{class_size}.csv"
        if self.group_matcher_output_data_file_path.exists():
            self.group_matcher_output_data_file_path.unlink()
        self.group_matcher_config_path = Path(self.group_matcher_run_path).parent / "example_config.py"
        if not self.group_matcher_input_data_file_path.parent.exists():
            self.group_matcher_input_data_file_path.parent.mkdir(parents=True)

    def export_students_data_to_group_matcher_format_csv(self, students: List[Student]) -> None:
        student_data = [GroupMatcherStudent(student).get_formatted_data() for student in students]
        self.student_trace = {student.id: student for student in students}
        with open(self.group_matcher_input_data_file_path, "w") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=student_data[0].keys(), delimiter=";"
            )
            writer.writeheader()
            writer.writerows(student_data)

    def generate(self, students: List[Student]) -> TeamSet:
        self.export_students_data_to_group_matcher_format_csv(students)

        # Run the group matcher algorithm
        cmd = f"python3 {self.group_matcher_run_path} {self.group_matcher_config_path} {self.group_matcher_input_data_file_path}"
        os.system(cmd)

        # This only happens when class size is small and the system I/O speed is not as fast as the runtime
        while not self.group_matcher_output_data_file_path.exists():
            print("Not found file " + str(self.group_matcher_output_data_file_path))
            time.sleep(1)
        # Read the output csv file and create a TeamSet
        df = pd.read_csv(self.group_matcher_output_data_file_path)

        return GroupMatcherStudent.transform_output_data_to_team_set(
            df,
            self.team_trace,
            self.student_trace,
            self.team_cycler
        )
