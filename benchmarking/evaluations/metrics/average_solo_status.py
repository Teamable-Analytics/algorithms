from collections import Counter
from typing import Dict, List

from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class AverageSoloStatus(TeamSetMetric):
    """
    Calculate the average number of students having solo status in a team
    """

    def __init__(self, minority_groups: Dict[int, List[int]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minority_groups = minority_groups

        if len(minority_groups) == 0:
            raise ValueError("minority_groups cannot be empty")

    def calculate(self, team_set: TeamSet) -> float:
        total_solo_status_students = set()
        total_students = 0.0
        for team in team_set.teams:
            for student in team.students:
                total_students += 1
                for attribute_id, attribute_groups in self.minority_groups.items():
                    # Create a dictionary of attribute_values and number of appearance in the team
                    all_attribute_values_in_team = Counter(
                        [
                            attr
                            for student in team.students
                            for attr in student.attributes.get(attribute_id)
                        ]
                    )

                    for attr in student.attributes.get(attribute_id):
                        if (
                            attr in self.minority_groups.get(attribute_id)
                            and all_attribute_values_in_team.get(attr) == 1
                        ):
                            total_solo_status_students.add(student.id)
                            break

        return len(total_solo_status_students) / float(total_students)