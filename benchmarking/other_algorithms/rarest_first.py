from typing import Dict, List

from benchmarking.simulation.simulation import Simulation, RunOutput
from models.enums import Relationship
from models.student import Student


class RarestFirstSimulation(Simulation):
    social_network: Dict[(str, str), Relationship] = {}

    def run(self, team_size: int) -> RunOutput:
        # Step 1: Set up
        student_list = self.student_provider.get()
        # 1a. Social network set up
        self._set_up_social_network(student_list)
        # 1b. Calculate the support for all
        
        pass

    def _set_up_social_network(self, student_list: List[Student]):
        for student in student_list:
            for other_student in student_list:
                if student.id == other_student.id:
                    continue

                if other_student.id in student.relationships:
                    self.social_network[(student.id, other_student.id)] = student.relationships.get(other_student.id)
                else:
                    self.social_network[(student.id, other_student.id)] = Relationship.DEFAULT

    @staticmethod
    def _get_supports(student_list: List[Student], attribute_id: int):
        supports: List[Student] = []

        for student in student_list:
            if attribute_id in student.attributes:
                supports.append(student)

        return supports
