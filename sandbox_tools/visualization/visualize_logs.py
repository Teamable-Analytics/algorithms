from typing import List, Dict

from sandbox_tools.algorithm_state import AlgorithmState
from sandbox_tools.logger import Logger
from team_generator.algorithm import FRIEND, ENEMY
from team_generator import Student
from team_generator.team import Team


class VisualizeLogs:
    def __init__(self, logger: Logger):
        self.all_students = logger.students
        self._student_cache: Dict[int, Student] = {}
        self.logger = logger
        self.state_index = 0
        self.algorithm_states: List[AlgorithmState] = [*logger.algorithm_states]
        self.nodes: List[Dict] = []
        self._nodes_cache: List[str] = []
        self.edges: List[Dict] = []

    def next(self):
        if self.state_index < len(self.algorithm_states):
            self.state_index += 1

    def prev(self):
        if self.state_index > 0:
            self.state_index -= 1

    def get_student_by_id(self, student_id: int):
        if student_id in self._student_cache:
            return self._student_cache[student_id]
        for student in self.all_students:
            if student.id == student_id:
                self._student_cache[student.id] = student
                return student
        raise ValueError(f'Cannot find student with id={student_id}')

    def get_current_team_compositions(self) -> List[Team]:
        return self.algorithm_states[self.state_index].current_team_compositions

    def get_current_stage(self) -> int:
        return self.algorithm_states[self.state_index].stage

    def student_currently_in_team(self, student_id: int):
        for team in self.get_current_team_compositions():
            if student_id in [student.id for student in team.students]:
                return True
        return False

    def state(self):
        return self.state_index

    def draw_student_node(self, student: Student):
        self.nodes.append({
            'id': student.id,
            'label': str(student.id),  # TODO: name?
            'color': self.get_node_colour(student)
        })

    def get_node_colour(self, student: Student):
        if self.student_currently_in_team(student.id):
            return 'grey'
        return 'rgb(97,195,238)'
    
    def draw_student_edge(self, src_student_node_id: int, dest_student_node_id: int, relationship: float):
        return self.edges.append({
            'id': f'{src_student_node_id}_{dest_student_node_id}',
            'from': src_student_node_id,
            'to': dest_student_node_id,
            'color': {'color': self.get_edge_colour(relationship)},  # TODO: investigate later
            })
    
    def get_edge_colour(self, relationship: float) -> str:
        if relationship == FRIEND:
            return 'green'
        if relationship == ENEMY:
            return 'red'
        raise ValueError(f'{relationship} is not a valid relationship value.')

    def draw_relationship_edge(self, src_student_node_id: int, dest_student_node_id: int, relationship: float):
        if src_student_node_id not in self._nodes_cache:
            self.draw_student_node(self.get_student_by_id(src_student_node_id))

        if dest_student_node_id not in self._nodes_cache:
            self.draw_student_node(self.get_student_by_id(dest_student_node_id))
            
        self.draw_student_edge(src_student_node_id, dest_student_node_id, relationship)
        
    def reset(self):
        self.nodes = []
        self.edges = []
        self._nodes_cache = []
        
        