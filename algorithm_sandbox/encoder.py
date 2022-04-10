from team_formation.app.team_generator.algorithm.consts import FRIEND
from team_formation.app.team_generator.student import Student

DATA_FILE_PATH = "algorithm_sandbox/mock_data/gen_group_set-20220331_141058.json"
KEY_FILE_PATH = "algorithm_sandbox/mock_data/student_key-20220331_141058.json"


class Encoder:
    STUDENT_KEY_CACHE = None

    @staticmethod
    def get_student_from_key(student_anon: Student, with_friends: bool = False):
        student_key = load_json_data(KEY_FILE_PATH)
        student_name = Encoder.get_real_student_name(student_key, student_anon.id)
        if not with_friends:
            return student_name

        friends = [
            Encoder.get_real_student_name(student_key, other_id) for other_id, relationship
            in student_anon.relationships.items() if relationship == FRIEND
        ]
        return f'{student_name} => Friends ({", ".join(friends)})'

    @staticmethod
    def get_real_student_name(student_key: dict, student_anon_id: int) -> str:
        for real_id, student_info in student_key.items():
            if student_info['anon_student_id'] == student_anon_id:
                return student_info['real_name']
        return f'Unknown Student ({student_anon_id})'

    @staticmethod
    def get_student_key():
        if Encoder.STUDENT_KEY_CACHE:
            return Encoder.STUDENT_KEY_CACHE
        student_key = load_json_data(KEY_FILE_PATH)
        Encoder.STUDENT_KEY_CACHE = student_key
        return student_key


def load_json_data(file_path: str):
    import json
    with open(file_path) as json_data:
        data = json.load(json_data)
        return data
