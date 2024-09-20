import csv
import os
from math import ceil
from os import path
from typing import List

import typer

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.models.enums import AlgorithmType, DiversifyType, ScenarioAttribute
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Goal, Scenario
from benchmarking.evaluations.metrics.cosine_similarity import \
    AverageCosineDifference
from benchmarking.runs.csv_weight_run_revised.attributes import Attributes
from benchmarking.runs.csv_weight_run_revised.data_provider_revised import \
    DataProvider
from benchmarking.runs.interfaces import Run
from benchmarking.simulation.insight import Insight
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
                attribute_filter=[ScenarioAttribute.TIMESLOT_AVAILABILITY.value],
            ),
        ]
        
        student_provider = DataProvider()
        team_size = 4 # enter the desired team size
        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=ceil(student_provider.num_students / team_size),
                scenario=scenario,
                student_provider=student_provider,
                cache_key=f"csv_weight_run_revised/weight_run_revised/",
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=15, # max num of solutions the algorithm is allowed to keep
                        MAX_SPREAD=30, # max num of team sets genereated by mutation at each step
                        MAX_ITERATE=30, # max num of iterations the algorithm is allowed to run
                        MAX_TIME=100000, # max time in seconds the algorithm can run for.
                    ),
                ]
            },
        ).run(num_runs=num_trials)

        team_set = list(artifact.values())[0][0][0]

        # Enter the data fields from the provided CSV file
        data_fields = [["ResponseId", "Q8", "Q4", "Q5", "zPos", "TeamSizeViolation", "TeamId"]]

        for team in team_set.teams:
            for student in team.students:
                attributes = student.attributes
                
                unique_id = student_provider.get_student(student.id)
                time_slot = attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value][0]
                tutor_preference = attributes[Attributes.TUTOR_PREFERENCE.value][0]
                group_size = attributes[Attributes.GROUP_SIZE.value][0]
                
                data_fields_input_1 = Attributes.revert_timeslot(time_slot)
                data_fields_input_2 = Attributes.revert_tutor_preference(tutor_preference)
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

                data_fields.append([unique_id, data_fields_input_1, data_fields_input_2, data_fields_input_3, positive_z, team_size_violation, team.id])
        # Directory where the new CSV file will be written
        output_dir = path.join(path.dirname(__file__), "new_csv")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, "result.csv")

        with open(output_file, "w+", newline="") as f:
            writer = csv.writer(f)
            for row in data_fields:
                writer.writerow(row)


class DefaultScenario(Scenario):
    @property
    def name(self) -> str:
        return "Diversify on score and concentrate on timeslot"

    @property
    def goals(self) -> List[Goal]:
        """
        This function is meant to create a list of scenerio goals to be followed for team formation.

        Returns:
            List[Goal]: A list of goals for team formation.
        """
        return [
            # Concentrate on student timeslot availability
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
            ),
            # Diversify students on tutor preference
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.TUTOR_PREFERENCE.value,
            ),
            # Diversify students on score
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.SCORE.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


# Run script from command line: python3 -m benchmarking.runs.csv_weight_run_revised.weight_run_revised
if __name__ == "__main__":
    typer.run(WeightRun().start)
