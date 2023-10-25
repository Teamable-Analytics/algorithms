"""
Rarest First Algorithm

TODO: Write up the algorithm steps here
"""
from typing import List, Dict, Set

from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_options import RarestFirstAlgorithmOptions
from api.ai.new.rarest_first_algorithm.custom_models import SupportGroup, Distance
from api.ai.new.rarest_first_algorithm.social_graph import RawSocialGraph
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet


class RarestFirstAlgorithm(Algorithm):
    def __init__(
        self, algorithm_options: RarestFirstAlgorithmOptions, team_generation_options
    ):
        super().__init__(algorithm_options, team_generation_options)

        self.attributes = algorithm_options.attributes

    def _get_students_with_attribute(
        self, students: List[Student], attribute_id: int
    ) -> SupportGroup:
        """
        Get support group for a given attribute
        """
        students_in_group = [
            student for student in students if attribute_id in student.attributes
        ]
        return SupportGroup(attribute_id, students_in_group)

    def _get_students_for_all_attributes(
        self, students: List[Student]
    ) -> Dict[int, SupportGroup]:
        """
        Get support groups for all attributes
        """
        students_for_all_attributes: Dict[int, SupportGroup] = {}
        for attribute_id in self.attributes:
            students_with_attribute = self._get_students_with_attribute(
                students, attribute_id
            )
            if students_with_attribute.value > 0:
                students_for_all_attributes[
                    attribute_id
                ] = self._get_students_with_attribute(students, attribute_id)

        return students_for_all_attributes

    def _get_least_supported_group(
        self, support_groups: Dict[int, SupportGroup]
    ) -> SupportGroup:
        """
        Get the group with the least number of students
        """
        return min(support_groups.values(), key=lambda group: group.value)

    def _get_max_distances(
        self,
        least_supported_group: SupportGroup,
        social_graph: RawSocialGraph,
        all_support_groups: Dict[int, SupportGroup],
    ):
        max_distance_of_each_student: Dict[int, Distance] = {}
        for student_lsg in least_supported_group.students:
            # student_lsg is the student in the least supported group

            max_distance = Distance(float("-inf"))

            for attribute_id in self.attributes:
                if attribute_id == least_supported_group.attribute_id:
                    continue

                current_support_group = all_support_groups.get(attribute_id)
                if not current_support_group:
                    continue

                for student_curr in current_support_group.students:
                    if student_curr.id == student_lsg.id:
                        continue

                    current_distance = social_graph.get_shortest_distance(
                        student_lsg, student_curr
                    )
                    if current_distance > max_distance.value:
                        max_distance.value = current_distance
                        max_distance.start_student = student_lsg
                        max_distance.end_student = student_curr
                        max_distance.is_updated = True

            if max_distance.is_updated:
                max_distance_of_each_student[student_lsg.id] = max_distance

        return max_distance_of_each_student

    def _build_shortest_distance_to_attribute_look_up(
        self,
        students: List[Student],
        support_groups: Dict[int, SupportGroup],
        social_graph: RawSocialGraph,
    ):
        distances: Dict[int, Dict[int, Distance]] = {
            student.id: {} for student in students
        }
        for student in students:
            for attribute_id in self.attributes:
                current_support_group = support_groups.get(attribute_id)
                if not current_support_group:
                    continue

                min_distance = Distance(float("inf"))
                for other in current_support_group.students:
                    if other.id == student.id:
                        continue

                    current_distance = social_graph.get_shortest_distance(
                        student, other
                    )
                    if current_distance < min_distance.value:
                        min_distance.value = current_distance
                        min_distance.start_student = student
                        min_distance.end_student = other
                        min_distance.is_updated = True

                if min_distance.is_updated:
                    distances[student.id][attribute_id] = min_distance

        return distances

    def generate(self, students: List[Student]) -> TeamSet:
        # Set up
        student_id_trace = {student.id: student for student in students}
        social_graph = RawSocialGraph(students)
        support_groups = self._get_students_for_all_attributes(students)
        least_supported_group = self._get_least_supported_group(support_groups)
        shortest_distance_to_attribute = (
            self._build_shortest_distance_to_attribute_look_up(
                students, support_groups, social_graph
            )
        )
        max_distances = self._get_max_distances(
            least_supported_group, social_graph, support_groups
        )

        # Run algorithm
        min_distance = Distance(float("inf"))  # i_star
        for student_id in max_distances:
            current_distance = max_distances[student_id]
            if current_distance.value < min_distance.value:
                min_distance = current_distance

        result: Set[int] = {min_distance.start_student.id}
        for attribute_id in self.attributes:
            distance_from_i_star = shortest_distance_to_attribute[
                min_distance.start_student.id
            ].get(attribute_id)
            if distance_from_i_star and distance_from_i_star.is_updated:
                result.add(distance_from_i_star.end_student.id)

        # The algorithm only returns one team
        self.teams[0].students = [
            student_id_trace.get(student_id) for student_id in result
        ]

        return TeamSet(teams=self.teams)
