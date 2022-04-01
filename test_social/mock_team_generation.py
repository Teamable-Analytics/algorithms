import math
from typing import List, Dict

from algorithm.algorithms import SocialAlgorithm, AlgorithmOptions
from algorithm.consts import FRIEND, ENEMY, DEFAULT
from student import Student
from team import Team
from team_generator import TeamGenerationOption, TeamGenerator

DATA_FILE_PATH = "test_social/mock_data/gen_group_set-20220331_141058.json"
KEY_FILE_PATH = "test_social/mock_data/student_key-20220331_141058.json"


class MockData:
    """
    File path should be from the root directory (where test.py is) and lead to a json file with the same structure as
    the one outputted from `group_data_retrieval <COURSE_ID> <GEN_GROUP_SET_ID>`
    """
    _fake_data_dict = {}
    STUDENT_ROLE = 'Student'
    RELATIONSHIP_ATTRIBUTE_TYPE = 'Include Friends/Exclude Enemies'
    PROJECT_PREF_ATTRIBUTE_TYPE = 'Project Preference'

    def __init__(self, file_path: str, total_teams: int):
        self._fake_data_dict = load_json_data(file_path)
        self.students = self.create_students()
        self.total_teams = total_teams

    @property
    def num_students(self) -> int:
        return len(self.students.values())

    def get_team_generation_option(self):
        team_generation_options = TeamGenerationOption(
            min_team_size=math.floor(self.num_students * 1.0 / self.total_teams),
            max_team_size=math.ceil(self.num_students * 1.0 / self.total_teams),
            total_teams=self.total_teams,
            team_options=[]
        )
        return team_generation_options

    def get_students(self) -> List[Student]:
        return [*self.students.values()]

    def create_students(self):
        student_dict = self.create_student_objects()
        for student_id, student_responses in self._fake_data_dict['student_responses'].items():
            student_id = int(student_id)
            if not self.is_student(student_id):
                continue
            student = student_dict[student_id]
            for attribute_id, response in student_responses.items():
                attribute_id = int(attribute_id)
                attribute_type = self.attribute_type(attribute_id)
                if attribute_type == self.PROJECT_PREF_ATTRIBUTE_TYPE:
                    continue  # TODO: ignore project preference for now
                if attribute_type == self.RELATIONSHIP_ATTRIBUTE_TYPE:
                    self.save_relationships(student, attribute_id, response)
                    continue  # don't save relationships as a skill
                student.skills.update({attribute_id: response})
        return student_dict

    def attribute_type(self, attribute_id: int) -> str:
        attribute_type = self._fake_data_dict['attribute_info'][f'{attribute_id}']['attr_type']
        return attribute_type

    def get_relationship_value(self, attribute_id: int):
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
        return self._fake_data_dict['student_info'][f'{student_id}']['role'] == MockData.STUDENT_ROLE

    def create_student_objects(self) -> Dict[int, Student]:
        student_dict = {}
        for student_id, student_info in self._fake_data_dict['student_info'].items():
            student_id = int(student_id)
            if not self.is_student(student_id):
                continue
            student_dict[student_id] = Student(student_id)
        return student_dict


def load_json_data(file_path: str):
    import json
    with open(file_path) as json_data:
        data = json.load(json_data)
        return data


def mock_generation(data_file_path: str = None):
    fake_data = MockData(data_file_path, 56)
    social_algorithm_options = AlgorithmOptions()
    social_algorithm = SocialAlgorithm(social_algorithm_options)  # needs algo options
    # team_generation_options = TeamGenerationOption(
    #     min_team_size=2,
    #     max_team_size=3,
    #     total_teams=2,
    #     team_options=[]
    # )
    # students = fake_custom_students()
    team_generation_options = fake_data.get_team_generation_option()
    students = fake_data.get_students()
    team_generator = TeamGenerator(students, social_algorithm, [], team_generation_options)

    return team_generator.generate()

