# import math
# from dataclasses import dataclass, field
# from time import time
#
# from typing import Dict, List, Set, Optional, Tuple
#
# from benchmarking.data.interfaces import MockStudentProviderSettings
# from benchmarking.data.simulated_data.mock_student_provider import MockStudentProvider
# from benchmarking.evaluations.graphing.graph_metadata import GraphData
# from benchmarking.evaluations.graphing.line_graph import line_graph
# from benchmarking.evaluations.graphing.line_graph_metadata import LineGraphMetadata
# from benchmarking.evaluations.scenarios.concentrate_all_attributes import (
#     ConcentrateAllAttributes,
# )
# from benchmarking.simulation.simulation import Simulation, RunOutput
# from models.enums import Relationship, ScenarioAttribute, AlgorithmType, Gender, Race
# from models.student import Student
#
# from heapq import heappush, heappop
#
#
# @dataclass(order=True)
# class Distance:
#     distance: float
#     start_student: int = field(compare=False)
#     end_student: int = field(compare=False)
#     path: List[int] = field(compare=False)
#
#
# def get_default_distance(value):
#     return Distance(distance=value, start_student=-1, end_student=-1, path=[])
#
#
# class RarestFirstSimulation(Simulation):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.social_network: Dict[Tuple[int, int], float] = {}
#
#     def run(self, team_size: int) -> RunOutput:
#         start_time = time()
#         # Step 1: Set up
#         student_list = self.student_provider.get()
#         # 1a. Social network set up
#         self._set_up_social_network(student_list)
#         # 1b. Calculate the support for all
#         support_groups = self._get_support_groups(student_list)
#
#         # Step 2: Get the lowest cardinality support
#         lowest_cardinality_group_attribute = min(
#             support_groups, key=lambda x: len(support_groups[x])
#         )
#         lowest_cardinality_group = support_groups[lowest_cardinality_group_attribute]
#
#         # Prebuild distance
#         distance_matrix: Dict[Tuple[int, int], Distance] = {}
#         for student in student_list:
#             for other_student in student_list:
#                 if student.id == other_student.id:
#                     continue
#
#                 distance_matrix[(student.id, other_student.id)] = self._find_distance(
#                     student_list,
#                     start_student_id=student.id,
#                     target_student_id=other_student.id,
#                 )
#
#         # Prebuild i/S(a) matrix
#         distance_to_support_group: Dict[Tuple[int, int], Distance] = {}
#         for student in student_list:
#             for attribute in ScenarioAttribute:
#                 support_group = support_groups.get(attribute.value, [])
#                 if not support_group:
#                     continue
#
#                 min_d: Distance = get_default_distance(float("inf"))
#                 for other_student in support_group:
#                     if other_student.id == student.id:
#                         continue
#                     distance = distance_matrix.get(
#                         (student.id, other_student.id), get_default_distance(-1)
#                     )
#                     if 0 <= distance.distance < min_d.distance:
#                         min_d = distance
#
#                 if min_d.distance != float("inf"):
#                     distance_to_support_group[(student.id, attribute.value)] = min_d
#
#         # Step 3: Run the algorithm
#         max_distances: Dict[int, Distance] = {}
#
#         for student in lowest_cardinality_group:
#             # R_ai
#             local_max_distance: Distance = get_default_distance(float("-inf"))
#             for attribute in ScenarioAttribute:
#                 if attribute.value == lowest_cardinality_group_attribute:
#                     continue
#                 current_support_group = self._get_support_group(
#                     student_list, attribute.value
#                 )
#
#                 for student_in_current_support_group in current_support_group:
#                     if student_in_current_support_group.id == student.id:
#                         continue
#
#                     current_distance = distance_matrix.get(
#                         (student.id, student_in_current_support_group.id), None
#                     )
#                     if not current_distance:
#                         continue
#
#                     if current_distance.distance > local_max_distance.distance:
#                         local_max_distance = current_distance
#
#             # i*
#             if local_max_distance.distance != float("-inf"):
#                 max_distances[student.id] = local_max_distance
#
#         # Find i*
#         i_star: Distance = get_default_distance(float("inf"))
#         for student_id, distance in max_distances.items():
#             if distance.distance == -1:
#                 continue
#
#             if i_star.distance > distance.distance:
#                 i_star = distance
#
#         # Step 4: Add all individuals along the path from i* to the support group for all attribute in attributes
#         result: Set[int] = {i_star.start_student}
#         for attribute in ScenarioAttribute:
#             distance_from_i_star = distance_to_support_group.get(
#                 (i_star.start_student, attribute.value), None
#             )
#             if distance_from_i_star:
#                 result.add(distance_from_i_star.end_student)
#
#         print("Result: " + str(result))
#         end_time = time()
#         self.run_outputs[AlgorithmType.RAREST_FIRST][Simulation.KEY_RUNTIMES] = [
#             end_time - start_time
#         ]
#         return self.run_outputs
#
#     def _set_up_social_network(self, student_list: List[Student]):
#         """
#         Based on each student's social preferences, construct a social network graph
#         """
#         for student in student_list:
#             for other_student in student_list:
#                 if student.id == other_student.id:
#                     continue
#
#                 # From original paper: The weights on the edges of G should be interpreted as follows: a low-weight
#                 # edge between nodes i, j implies that candidate i and j can collaborate and/or communicate more
#                 # easily than candidates connected with a high-weight edge.
#                 relationship = student.relationships.get(other_student.id)
#                 if relationship:
#                     self.social_network[
#                         (student.id, other_student.id)
#                     ] = relationship.value
#                 else:
#                     self.social_network[
#                         (student.id, other_student.id)
#                     ] = Relationship.DEFAULT.value
#
#                 # Since Dijkstra's algorithm cannot handle negative weight, for this graph, we use these values:
#                 #   - FRIEND: 0.0
#                 #   - DEFAULT: 1.0
#                 #   - ENEMY: 2.1
#                 self.social_network[
#                     (student.id, other_student.id)
#                 ] += -Relationship.FRIEND.value
#
#     @staticmethod
#     def _get_support_group(student_list: List[Student], attribute_id: int):
#         supports: List[Student] = []
#
#         for student in student_list:
#             if attribute_id in student.attributes:
#                 supports.append(student)
#
#         return supports
#
#     @staticmethod
#     def _get_support_groups(student_list: List[Student]) -> Dict[int, List[Student]]:
#         support_groups = {}
#         for attribute in ScenarioAttribute:
#             support_group = RarestFirstSimulation._get_support_group(
#                 student_list, attribute.value
#             )
#             if len(support_group) == 0:
#                 continue
#
#             support_groups[attribute.value] = support_group
#
#         return support_groups
#
#     def _find_distance(
#         self, student_list: List[Student], start_student_id: int, target_student_id: int
#     ) -> Optional[Distance]:
#         """
#         Dijkstra's algorithm implementation
#         """
#
#         # Set up
#         distances: List[Distance] = []
#         visited: Set[int] = set()
#         for student in student_list:
#             if student.id == start_student_id:
#                 heappush(
#                     distances,
#                     Distance(
#                         distance=0,
#                         start_student=start_student_id,
#                         end_student=start_student_id,
#                         path=[start_student_id],
#                     ),
#                 )
#         visited.add(start_student_id)
#
#         # Dijkstra's algorithm
#         while len(visited) < len(student_list):
#             shortest_distance: Distance = heappop(distances)
#             if shortest_distance.end_student == target_student_id:
#                 return shortest_distance
#
#             next_student_id = shortest_distance.end_student
#             visited.add(next_student_id)
#
#             for student in student_list:
#                 if student.id in visited:
#                     continue
#
#                 heappush(
#                     distances,
#                     Distance(
#                         distance=shortest_distance.distance
#                         + self.social_network[(next_student_id, student.id)],
#                         start_student=start_student_id,
#                         end_student=student.id,
#                         path=shortest_distance.path + [student.id],
#                     ),
#                 )
#
#         # Not connected case
#         return get_default_distance(-1)
#
#
# if __name__ == "__main__":
#     CLASS_SIZES = [8, 12, 16, 20, 40, 60, 80, 100]
#     # CLASS_SIZES = [8, 12, 16, 20]
#     TEAM_SIZE = 4
#     MAX_NUM_PROJECT_PREFERENCES = 3
#
#     # Graph variables
#     graph_data_dict: Dict[AlgorithmType, GraphData] = {}
#
#     for class_size in CLASS_SIZES:
#         print(f"Class size: {class_size}")
#
#         number_of_teams = math.ceil(class_size / 4)
#         ratio_of_female_students = 0.5
#
#         mock_num_projects = math.ceil(
#             number_of_teams * 1.5
#         )  # number of project should be more than number of teams
#         mock_project_list = [i + 1 for i in range(mock_num_projects)]
#
#         student_provider_settings = MockStudentProviderSettings(
#             number_of_students=class_size,
#             number_of_friends=4,
#             number_of_enemies=1,
#             num_values_per_attribute={
#                 ScenarioAttribute.PROJECT_PREFERENCES.value: MAX_NUM_PROJECT_PREFERENCES,
#             },
#             attribute_ranges={
#                 ScenarioAttribute.AGE.value: list(range(20, 24)),
#                 ScenarioAttribute.GENDER.value: [
#                     (Gender.MALE, 1 - ratio_of_female_students),
#                     (Gender.FEMALE, ratio_of_female_students),
#                 ],
#                 ScenarioAttribute.GPA.value: list(range(60, 100)),
#                 ScenarioAttribute.RACE.value: list(range(len(Race))),
#                 ScenarioAttribute.MAJOR.value: list(range(1, 4)),
#                 ScenarioAttribute.YEAR_LEVEL.value: list(range(3, 5)),
#                 ScenarioAttribute.PROJECT_PREFERENCES.value: mock_project_list,
#             },
#         )
#
#         simulation_outputs = RarestFirstSimulation(
#             num_teams=number_of_teams,
#             scenario=ConcentrateAllAttributes(),
#             student_provider=MockStudentProvider(student_provider_settings),
#             metrics=[],
#             algorithm_types=[AlgorithmType.RAREST_FIRST],
#         ).run(team_size=TEAM_SIZE)
#
#         average_runtimes = Simulation.average_metric(simulation_outputs, "runtimes")
#
#         # Data processing for graph
#         for algorithm_type, average_runtime in average_runtimes.items():
#             if algorithm_type not in graph_data_dict:
#                 graph_data_dict[algorithm_type] = GraphData(
#                     x_data=[class_size],
#                     y_data=[average_runtime],
#                     name=algorithm_type.value,
#                 )
#             else:
#                 graph_data_dict[algorithm_type].x_data.append(class_size)
#                 graph_data_dict[algorithm_type].y_data.append(average_runtime)
#
#     line_graph(
#         LineGraphMetadata(
#             x_label="Class size",
#             y_label="Run time (seconds)",
#             title="Run RareFirst algorithm",
#             data=list(graph_data_dict.values()),
#             description=None,
#             y_lim=None,
#             x_lim=None,
#         )
#     )
