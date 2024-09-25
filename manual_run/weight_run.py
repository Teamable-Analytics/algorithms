import csv
import os
from math import ceil
from os import path

import typer
from manual_run.attributes import Attributes
from manual_run.data_provider import DataProvider
from manual_run.default_scenario import DefaultScenario
from manual_run.variables import Variables

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import AlgorithmType
from benchmarking.evaluations.metrics.cosine_similarity import \
    AverageCosineDifference
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.simulation_set import (SimulationSet,
                                                    SimulationSetArtifact)
from benchmarking.simulation.simulation_settings import SimulationSettings


class WeightRun(Run):
    
    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = DefaultScenario()

        # Metrics to be used for evaluation
        metrics = [
            AverageCosineDifference(
                name="Score Cosine Difference",
                attribute_filter=[Attributes.SCORE.value],
            ),
            AverageCosineDifference(
                name="Timeslot Cosine Difference",
                attribute_filter=[Attributes.TIMESLOT_AVAILABILITY.value],
            ),
        ]
        student_provider = DataProvider()
        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=ceil(student_provider.num_students / Variables.team_size),
                scenario=scenario,
                student_provider=student_provider,
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=15,  # max num of solutions the algorithm is allowed to keep
                        MAX_SPREAD=30,  # max num of team sets genereated by mutation at each step
                        MAX_ITERATE=30,  # max num of iterations the algorithm is allowed to run
                        MAX_TIME=100000,  # max time in seconds the algorithm can run for.
                    ),
                ]
            },
        ).run(num_runs=1)
        team_set = list(artifact.values())[0][0][0]

        self.create_csv(team_set, student_provider)
        
        
    def create_csv(self, team_set, student_provider):
        Variables.data_fields[0].append("TeamSizeViolation")
        Variables.data_fields[0].append("TeamId")
        
        for team in team_set.teams:
            for student in team.students:
                attributes = student.attributes

                unique_id = student_provider.get_student(student.id)
                time_slot = attributes[Attributes.TIMESLOT_AVAILABILITY.value][0]
                tutor_preference = attributes[Attributes.TUTOR_PREFERENCE.value][0]
                group_size = attributes[Attributes.GROUP_SIZE.value][0]

                data_fields_input_1 = Attributes.revert_timeslot(time_slot)
                data_fields_input_2 = Attributes.revert_tutor_preference(
                    tutor_preference
                )
                data_fields_input_3 = Attributes.revert_group_size(group_size)

                # Process score and team size violation
                positive_z = "1" if attributes[Attributes.SCORE.value][0] == 1 else "0"
                num_teams = len(team.students)

                # Can be customize to fit the team size preference
                team_size_violation = (
                    "Yes"
                    if tutor_preference == 3
                    and (
                        (group_size == 1 and num_teams != 2)
                        or (group_size == 2 and (num_teams > 4 or num_teams < 3))
                        or (group_size == 3 and num_teams < 4)
                    )
                    else ""
                )

                Variables.data_fields.append(
                    [
                        unique_id,
                        data_fields_input_1,
                        data_fields_input_2,
                        data_fields_input_3,
                        positive_z,
                        team_size_violation,
                        team.id,
                    ]
                )
        # Directory where the new CSV file will be written
        output_dir = path.join(path.dirname(__file__), "new_csv_output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, Variables.output_file_name)
        
        with open(output_file, "w+", newline="") as f:
            writer = csv.writer(f)
            for row in Variables.data_fields:
                writer.writerow(row)


if __name__ == "__main__":
    typer.run(WeightRun().start)
