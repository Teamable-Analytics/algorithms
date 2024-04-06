import csv
import itertools
import os
import time
from pathlib import Path
from typing import List, Dict

import pandas as pd

from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.algorithm_config import GroupMatcherAlgorithmConfig
from api.ai.interfaces.algorithm_options import GroupMatcherAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.enums import ScenarioAttribute, fromAlRaceToRace, fromAlGenderToGender
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class GroupMatcherAlgorithm(Algorithm):
    student_trace: Dict[int, Student]

    def __init__(
        self,
        algorithm_options: GroupMatcherAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        algorithm_config: GroupMatcherAlgorithmConfig,
        *args,
        **kwargs,
    ):
        super().__init__(algorithm_options, team_generation_options, algorithm_config)
        self.csv_input_path = Path(algorithm_config.csv_input_path)

        class_size = int(self.csv_input_path.stem.split("-")[0])
        self.group_matcher_run_path = algorithm_config.group_matcher_run_path
        self.outpath = Path.cwd() / f"out-private-{class_size}.csv"
        if self.outpath.exists():
            self.outpath.unlink()
        self.config_file_path = (
            Path(self.group_matcher_run_path).parent / "example_config.py"
        )

        self.team_trace = {team_idx + 1: team for team_idx, team in enumerate(self.teams)}
        self.team_cycler = itertools.cycle(self.teams)

        if not self.csv_input_path.parent.exists():
            self.csv_input_path.parent.mkdir(parents=True)

    def prepare(self, students: List[Student]) -> None:
        student_data = [student.to_group_matcher_data_format() for student in students]
        self.student_trace = {student.id: student for student in students}
        with open(self.csv_input_path, "w") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=student_data[0].keys(), delimiter=";"
            )
            writer.writeheader()
            writer.writerows(student_data)

    def generate(self, students: List[Student]) -> TeamSet:
        # Run the group matcher algorithm
        cmd = f"python3 {self.group_matcher_run_path} {self.config_file_path} {self.csv_input_path}"
        os.system(cmd)

        # Read the output csv file and create a TeamSet
        while not self.outpath.exists():
            print("Not found file " + str(self.outpath))
            time.sleep(1)
        df = pd.read_csv(self.outpath)
        for _, row in df.iterrows():
            student_id = row["sid"]
            group_num = int(row["group_num"]) + 1
            if group_num not in self.team_trace.keys():
                new_team_attributes = self.team_cycler.__next__()
                new_team = Team(
                    _id=len(self.team_trace) + 1,
                    name=f"Team {len(self.team_trace) + 1}",
                    requirements=new_team_attributes.requirements,
                    project_id=new_team_attributes.project_id,
                    students=[],
                )
                self.team_trace[int(row["group_num"]) + 1] = new_team

            student = self.student_trace[student_id]
            team = self.team_trace[int(row["group_num"]) + 1]

            student.add_team(team)
            team.add_student(student)

        return TeamSet(teams=[team for team in self.teams if len(team.students) > 0])