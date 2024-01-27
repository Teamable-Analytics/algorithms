from collections import Counter
from typing import Dict, List

from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageSoloStatus(TeamSetMetric):
    def __init__(self, minority_groups: Dict[int, List[int]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minority_groups = minority_groups

        if len(minority_groups) == 0:
            raise ValueError("minority_groups cannot be empty")

    def calculate(self, team_set: TeamSet) -> float:
        total = 0.0
        for team in team_set.teams:
            is_solo = False
            for attribute_id, attribute_groups in self.minority_groups.items():
                all_attribute_values_in_team = Counter(
                    [
                        attr
                        for student in team.students
                        for attr in student.attributes.get(attribute_id)
                    ]
                )

                for attribute_group in attribute_groups:
                    if (
                        attribute_group in all_attribute_values_in_team
                        and all_attribute_values_in_team.get(attribute_group) == 1
                    ):
                        is_solo = True
                        break
            if is_solo:
                total += 1
        return total / float(len(team_set.teams))
