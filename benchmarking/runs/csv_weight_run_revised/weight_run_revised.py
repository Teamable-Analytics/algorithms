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
        print("student provider: ",student_provider.num_students)
        team_size = 4 # enter the desired team size
        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=ceil(student_provider.num_students / team_size),
                scenario=scenario,
                student_provider=student_provider,
                cache_key=f"weight_run_for_bowen/weight_run_2/",
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=15, # max num of solutions the algorithm is allowed to keep
                        MAX_SPREAD=30, # max num of of team sets genereated by mutation at each step
                        MAX_ITERATE=30, # max num of iterations the algorithm is allowed to run
                        MAX_TIME=100000, # max time is seconds to algorithm can run for.
                    ),
                ]
            },
        ).run(num_runs=num_trials)

        team_set = list(artifact.values())[0][0][0]

        insight_output_set = Insight.get_output_set(artifact, metrics)

        data = [["ResponseId", "Q8", "Q4", "Q5", "zPos", "TeamId", "TeamSizeViolation"]]

        for team in team_set.teams:
            for student in team.students:
                attributes = student.attributes

                responseId = student_provider.get_student(student.id)

                timeslot = attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value][0]
                q8 = (
                    "In-person before or after class"
                    if timeslot == 1
                    else (
                        "In-person nights or weekends" if timeslot == 2 else "On zoom"
                    )
                )

                tutor_preference = attributes[Attributes.TUTOR_PREFERENCE.value][0]
                q4 = (
                    "I am looking for a classmate to tutor me in BIOC 202"
                    if tutor_preference == 1
                    else (
                        "I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee"
                        if tutor_preference == 2
                        else "I am interested in being a peer tutor in BIOC 202"
                    )
                )

                group_size = attributes[Attributes.GROUP_SIZE.value][0]
                q5 = (
                    "1"
                    if group_size == 1
                    else (
                        "2 to 3"
                        if group_size == 2
                        else ("3+" if group_size == 3 else "")
                    )
                )

                zPos = "1" if attributes[Attributes.SCORE.value][0] == 1 else "0"

                team_size = len(team.students)
                teamSizeViolation = (
                    "Yes"
                    if tutor_preference == 3
                    and (
                        (group_size == 1 and team_size != 2)
                        or (group_size == 2 and (team_size > 4 or team_size < 3))
                        or (group_size == 3 and team_size < 4)
                    )
                    else ""
                )

                data.append([responseId, q8, q4, q5, zPos, team.id, teamSizeViolation])
        # Directory where the new CSV file will be written
        output_dir = path.join(path.dirname(__file__), "new_csv")

        # Ensure the directory exists, if not, create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Path to the new CSV file in the 'new_csv' folder
        output_file = os.path.join(output_dir, "result.csv")

        # Writing the CSV data into the file in the 'new_csv' folder
        with open(output_file, "w+", newline="") as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)


class DefaultScenario(Scenario):
    @property
    def name(self) -> str:
        return "Diversify on score and concentrate on timeslot"

    @property
    def goals(self) -> List[Goal]:
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


if __name__ == "__main__":
    typer.run(WeightRun().start)
