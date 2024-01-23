import csv
import os
from pathlib import Path
from typing import List

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
    def __init__(
        self,
        algorithm_options: GroupMatcherAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
        algorithm_config: GroupMatcherAlgorithmConfig,
        *args,
        **kwargs,
    ):
        super().__init__(algorithm_options, team_generation_options, algorithm_config)
        self.csv_input_path = algorithm_config.csv_input_path
        self.group_matcher_run_path = algorithm_config.group_matcher_run_path
        self.outpath = Path.cwd() / "out-private.csv"
        if self.outpath.exists():
            self.outpath.unlink()
        self.config_file_path = (
            Path(self.group_matcher_run_path).parent / "example_config.py"
        )

        self.team_trace = {team.id: team for team_idx, team in enumerate(self.teams)}

        if not self.csv_input_path.parent.exists():
            self.csv_input_path.parent.mkdir(parents=True)

    def prepare(self, students: List[Student]) -> None:
        student_data = [student.to_group_matcher_data_format() for student in students]
        with open(self.csv_input_path, "w") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=student_data[0].keys(), delimiter=";"
            )
            writer.writeheader()
            writer.writerows(student_data)

    def generate(self, students: List[Student]) -> TeamSet:
        # Run the group matcher algorithm
        cmd = f"python3 {self.group_matcher_run_path} {self.config_file_path} {self.csv_input_path}"
        print(cmd)
        cmd_output = os.system(cmd)
        print(cmd_output)

        # Read the output csv file and create a TeamSet
        df = pd.read_csv(self.outpath)
        for _, row in df.iterrows():
            new_student = Student(
                _id=row["sid"],
                name=row["first_name"] + " " + row["last_name"],
                attributes={
                    ScenarioAttribute.YEAR_LEVEL.value: [int(row["year"])],
                    ScenarioAttribute.RACE.value: [
                        fromAlRaceToRace(int(row["race"])).value
                    ],
                    ScenarioAttribute.GENDER.value: [
                        fromAlGenderToGender(int(row["gender"])).value
                    ],
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: list(
                        map(int, row["disc_times_options"].strip("[']").split(","))
                    ),
                },
            )

            self.team_trace[int(row["group_num"]) + 1].add_student(new_student)

        return TeamSet(teams=self.teams)
