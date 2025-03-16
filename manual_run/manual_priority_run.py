import csv
import os
from math import ceil
from os import path

import typer

from algorithms.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from algorithms.dataclasses.enums import AlgorithmType
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.simulation_set import SimulationSet, SimulationSetArtifact
from benchmarking.simulation.simulation_settings import SimulationSettings
from manual_run.attributes import Attributes
from manual_run.data_provider import DataProvider
from manual_run.default_scenario import DefaultScenario
from manual_run.map_columns import revert_value
from manual_run.variables import Variables


class ManualPriorityRun(Run):
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

        self.create_csv(team_set)

    def create_csv(self, team_set):
        """
        The generated CSV file will include the 'responseId' and the data fields specified in
        Variables.attribute_options and Variables.attribute_handlers. These fields will be written
        in the same order as they appear in the variables.py script. Additionally, two extra columns,
        'TeamSizeViolation' and 'TeamId', will be appended to the file.
        """
        data_fields = [["ResponseId"]]
        for key in Variables.attribute_options:
            data_fields[0].append(key)
        for key in Variables.attribute_handlers:
            data_fields[0].append(key)

        # if TeamSizeViolation is not needed then the following line can be deleted
        data_fields[0].append("TeamSizeViolation")
        data_fields[0].append("TeamId")

        for team in team_set.teams:
            for student in team.students:
                attributes = student.attributes

                time_slot = attributes[Attributes.TIMESLOT_AVAILABILITY.value][0]
                tutor_preference = attributes[Attributes.TUTOR_PREFERENCE.value][0]
                group_size = attributes[Attributes.GROUP_SIZE.value][0]

                data_fields_input_1 = revert_value("Q8", time_slot)
                data_fields_input_2 = revert_value("Q4", tutor_preference)
                data_fields_input_3 = revert_value("Q5", group_size)

                team_size = len(team.students)

                """ 
                The team size violation is calculated based on the tutor's preference and the group size
                to ensure that the team size falls within an acceptable range. If monitoring team size 
                violations is no longer necessary, this calculation can be removed. Additionally, any 
                changes to the data fields will require corresponding updates to this logic.
                """
                team_size_violation = (
                    "Yes"
                    if tutor_preference == 2
                    and (
                        (group_size == 0 and team_size != 2)
                        or (group_size == 1 and (team_size > 4 or team_size < 3))
                        or (group_size == 2 and team_size < 4)
                    )
                    else ""
                )

                data_fields.append(
                    [
                        student.id,
                        data_fields_input_1,
                        data_fields_input_2,
                        data_fields_input_3,
                        attributes[Attributes.SCORE.value][0],
                        team_size_violation,  # if TeamSizeViolation is not needed delete this line
                        team.id,
                    ]
                )
        # Directory where the new CSV file will be written
        output_dir = path.dirname(__file__)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, Variables.output_file_name)

        with open(output_file, "w+", newline="") as f:
            writer = csv.writer(f)
            for row in data_fields:
                writer.writerow(row)


if __name__ == "__main__":
    typer.run(ManualPriorityRun().start)
