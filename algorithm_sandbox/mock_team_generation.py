import math
from typing import List, Dict

from team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions
from team_formation.app.team_generator.algorithm.consts import FRIEND, ENEMY, DEFAULT
from team_formation.app.team_generator.algorithm.social_algorithm.social_algorithm import SocialAlgorithm
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team_generator import TeamGenerationOption, TeamGenerator
from algorithm_sandbox.encoder import Encoder, load_json_data


class MockData:
    """
    File path should be from the root directory (where test.py is) and lead to a json file with the same structure as
    the one outputted from `group_data_retrieval <COURSE_ID> <GEN_GROUP_SET_ID>`
    """
    _fake_data_dict = {}
    _students = {}
    STUDENT_ROLE = 'Student'
    RELATIONSHIP_ATTRIBUTE_TYPE = 'Include Friends/Exclude Enemies'
    PROJECT_PREF_ATTRIBUTE_TYPE = 'Project Preference'

    def __init__(self, total_teams: int, file_path: str = None, students: List[Student] = None, team_options: [] = None):
        if not students and not file_path:
            raise Exception('One of "students" or "file_path" must be defined.')

        if file_path:
            self._fake_data_dict = load_json_data(file_path)

        self.students = students if students else self.create_students()
        self.total_teams = total_teams
        self.team_options = team_options if team_options else []

    def get_students(self) -> List[Student]:
        return self.students

    @property
    def num_students(self) -> int:
        return len(self.students)

    def get_team_generation_option(self) -> TeamGenerationOption:
        team_generation_options = TeamGenerationOption(
            min_team_size=math.floor(self.num_students * 1.0 / self.total_teams),
            max_team_size=math.ceil(self.num_students * 1.0 / self.total_teams),
            total_teams=self.total_teams,
            team_options=self.team_options
        )
        return team_generation_options

    def create_students(self) -> List[Student]:
        self._students = self.create_student_objects()
        for student_id, student_responses in self._fake_data_dict['student_responses'].items():
            student_id = int(student_id)
            if not self.is_student(student_id):
                continue
            student = self._students[student_id]
            for attribute_id, response in student_responses.items():
                attribute_id = int(attribute_id)
                attribute_type = self.attribute_type(attribute_id)
                if attribute_type == self.PROJECT_PREF_ATTRIBUTE_TYPE:
                    continue  # TODO: ignore project preference for now
                if attribute_type == self.RELATIONSHIP_ATTRIBUTE_TYPE:
                    self.save_relationships(student, attribute_id, response)
                    continue  # don't save relationships as a skill
                student.skills.update({attribute_id: response})
        return [*self._students.values()]

    def attribute_type(self, attribute_id: int) -> str:
        attribute_type = self._fake_data_dict['attribute_info'][f'{attribute_id}']['attr_type']
        return attribute_type

    def get_relationship_value(self, attribute_id: int) -> float:
        # TODO: remove, this is specific and depends on the data itself.
        #  we should change this so that the data stores if the attribute is a friend or enemy and this method just
        #  retrieves that and converts that into the corresponding float value
        if attribute_id == 74:
            return FRIEND
        if attribute_id == 75:
            return ENEMY
        return DEFAULT

    def save_relationships(self, student: Student, attribute_id: int, relationships: List[int]):
        if not relationships:
            return
        relationship_value = self.get_relationship_value(attribute_id)
        for other_id in relationships:
            student.relationships.update({other_id: relationship_value})

    def is_student(self, student_id: int) -> bool:
        student_data = self._fake_data_dict['student_info'][f'{student_id}']
        student_name = Encoder.get_student_name_by_id(Encoder.get_student_key(), student_id)
        if student_name is None:
            return False
        return student_data['role'] == MockData.STUDENT_ROLE

    def create_student_objects(self) -> Dict[int, Student]:
        student_dict = {}
        for student_id, student_info in self._fake_data_dict['student_info'].items():
            student_id = int(student_id)
            if not self.is_student(student_id):
                continue
            student_dict[student_id] = Student(student_id)
        return student_dict


def mock_generation(logger, num_teams: int, data_file_path: str = None):
    fake_data = MockData(num_teams, data_file_path)
    social_algorithm_options = AlgorithmOptions()
    social_algorithm = SocialAlgorithm(social_algorithm_options, logger)  # needs algo options
    team_generation_options = fake_data.get_team_generation_option()
    students = fake_data.get_students()
    team_generator = TeamGenerator(students, social_algorithm, [], team_generation_options)

    return team_generator.generate()

