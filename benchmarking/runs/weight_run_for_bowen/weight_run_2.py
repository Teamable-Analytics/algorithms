from math import ceil
from typing import List

import typer
import csv

from api.ai.interfaces.algorithm_config import (
    PriorityAlgorithmConfig,
)
from api.models.enums import AlgorithmType, DiversifyType, ScenarioAttribute
from benchmarking.evaluations.goals import DiversityGoal, WeightGoal
from benchmarking.evaluations.interfaces import Scenario, Goal
from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.runs.interfaces import Run
from benchmarking.runs.weight_run_for_bowen.bowens_data_provider import (
    Attributes,
    BowensDataProvider2,
)
from benchmarking.simulation.insight import Insight
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class WeightRun(Run):
    def start(self, num_trials: int = 1, generate_graphs: bool = True):
        scenario = BowenScenario2()

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

        student_provider = BowensDataProvider2()

        artifact: SimulationSetArtifact = SimulationSet(
            settings=SimulationSettings(
                num_teams=ceil(student_provider.num_students / 4),
                scenario=scenario,
                student_provider=student_provider,
                cache_key=f"weight_run_for_bowen/weight_run_2/",
            ),
            algorithm_set={
                AlgorithmType.PRIORITY: [
                    PriorityAlgorithmConfig(
                        MAX_KEEP=15,
                        MAX_SPREAD=30,
                        MAX_ITERATE=30,
                        MAX_TIME=100000,
                    ),
                ]
            },
        ).run(num_runs=num_trials)

        team_set = list(artifact.values())[0][0][0]

        insight_output_set = Insight.get_output_set(artifact, metrics)
        print(insight_output_set)

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

        with open("result.csv", "w+", newline="") as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)


class BowenScenario2(Scenario):
    @property
    def name(self) -> str:
        return "Diversify on score and concentrate on timeslot"

    @property
    def goals(self) -> List[Goal]:
        return [
            DiversityGoal(
                DiversifyType.CONCENTRATE,
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.TUTOR_PREFERENCE.value,
            ),
            DiversityGoal(
                DiversifyType.DIVERSIFY,
                Attributes.SCORE.value,
            ),
            WeightGoal(diversity_goal_weight=1),
        ]


if __name__ == "__main__":
    typer.run(WeightRun().start)
