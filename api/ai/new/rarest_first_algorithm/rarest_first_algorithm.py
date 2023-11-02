"""
Rarest First Algorithm
This algorithm aims to generate a team of friends with all the attributes satisfied the requirement of a project.

Assumptions:
- We have a social network of students with node is a student and edge is the relationship between two students:
    - If a student is a friend of another student, the edge has negative weight (we use -1)
    - If a student is not a friend of another student, the edge has positive weight (we use 1.1)
    - If they are neither friend nor not friend, the edge has neutral weight (we use 0)
- Because Dijkstra's algorithm requires all edges to be positive, we add the value of 1 to all edges
- We know the shortest distance between a student i with a support group of attribute a (we call it d(i, a)). This means
we know who is the closest to student i having attribute a.

Algorithm:
For each attribute a in project_requirement:
    Find the support group of attribute a (we call it S(a))

Compute the shortest distance between each student i and each S(a) with all a in project_requirement (we call it d(i, a))

Find the attribute a_rare, meaning S(a_rare) is smallest

For each student i in S(a_rare):
    For each attribute a in project_requirement that is not a_rare:
        R(i, a) = d(i, a)
    Find R(i) = max(R(i, a)) with all a in project_requirement that is not a_rare

Find i_star = min(R(i)) with all i in S(a_rare)

The team is:
    - i_star
    - Path from i_star to each closest student in S(a) with all a in project_requirement that is not a_rare
"""
from typing import List, Dict, Set

from api.ai.new.interfaces.algorithm import Algorithm
from api.ai.new.interfaces.algorithm_options import RarestFirstAlgorithmOptions
from api.ai.new.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.new.rarest_first_algorithm.custom_models import SupportGroup, Distance
from api.ai.new.rarest_first_algorithm.social_graph import RawSocialGraph
from api.models.project import ProjectRequirement
from api.models.student import Student
from api.models.team_set import TeamSet


class RarestFirstAlgorithm(Algorithm):
    def __init__(
        self,
        algorithm_options: RarestFirstAlgorithmOptions,
        team_generation_options: TeamGenerationOptions,
    ):
        super().__init__(algorithm_options, team_generation_options)
        # This algorithm needs custom validation because of it is not a team generation algorithm
        self._validate()

        self.requirements = team_generation_options.initial_teams[0].requirements

    def _validate(self):
        if self.team_generation_options.total_teams != 1:
            raise ValueError(
                f"RarestFirstAlgorithm only supports total_teams = 1, got {self.team_generation_options.total_teams}"
            )
        if self.team_generation_options.initial_teams is None:
            raise ValueError(
                f"RarestFirstAlgorithm requires initial_teams to be passed in, got None"
            )
        if self.team_generation_options.initial_teams[0].requirements is None:
            raise ValueError(
                f"RarestFirstAlgorithm requires initial_teams[0].requirements to be passed in, got None"
            )

    def _get_students_with_attribute(
        self, students: List[Student], requirement: ProjectRequirement
    ) -> SupportGroup:
        """
        Get support group for a given attribute
        """
        students_in_group = [
            student for student in students if student.meets_requirement(requirement)
        ]
        return SupportGroup(requirement, students_in_group)

    def _get_students_for_all_attributes(
        self, students: List[Student]
    ) -> Dict[int, SupportGroup]:
        """
        Get support groups for all attributes
        """
        students_for_all_attributes: Dict[int, SupportGroup] = {}
        requirements = self.teams[0].requirements
        for requirement in requirements:
            students_with_attribute = self._get_students_with_attribute(
                students, requirement
            )
            if students_with_attribute.value > 0:
                students_for_all_attributes[
                    requirement.attribute
                ] = students_with_attribute

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

            for requirement in self.requirements:
                if requirement.attribute == least_supported_group.requirement.attribute:
                    continue

                current_support_group = all_support_groups.get(requirement.attribute)
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
            for requirement in self.requirements:
                current_support_group = support_groups.get(requirement.attribute)
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
                    distances[student.id][requirement.attribute] = min_distance

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
        for requirement in self.requirements:
            if requirement.attribute == least_supported_group.requirement.attribute:
                continue
            distance_from_i_star = shortest_distance_to_attribute[
                min_distance.start_student.id
            ].get(requirement.attribute)
            if distance_from_i_star and distance_from_i_star.is_updated:
                result.add(distance_from_i_star.end_student.id)

        # The algorithm only returns one team
        self.teams[0].students = [
            student_id_trace.get(student_id) for student_id in result
        ]

        return TeamSet(teams=self.teams)
