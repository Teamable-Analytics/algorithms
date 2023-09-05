from old.team_formation.app.team_generator.student import Student

DATA_FILE_PATH = "old/algorithm_sandbox/mock_data/gen_group_set-20220331_141058.json"
KEY_FILE_PATH = "old/algorithm_sandbox/mock_data/student_key-20220331_141058.json"


class Encoder:
    STUDENT_KEY_CACHE = None

    @staticmethod
    def get_student_name(student_anon: Student) -> str:
        return f"Student ({student_anon.id})"
        # student_key = load_json_data(KEY_FILE_PATH)
        # student_name = Encoder.get_student_name_by_id(student_key, student_anon.id)
        # return student_name

    @staticmethod
    def get_student_name_by_id(student_key: dict, student_anon_id: int) -> str:
        return f"Student ({student_anon_id})"
        # for real_id, student_info in student_key.items():
        #     if student_info['anon_student_id'] == student_anon_id:
        #         student_name = student_info['real_name']
        #         return student_name if student_name else f'No Name ({real_id})'
        # return f'Unknown Student ({student_anon_id})'

    @staticmethod
    def get_student_key():
        return {}
        # if Encoder.STUDENT_KEY_CACHE:
        #     return Encoder.STUDENT_KEY_CACHE
        # student_key = load_json_data(KEY_FILE_PATH)
        # Encoder.STUDENT_KEY_CACHE = student_key
        # return student_key


def load_json_data(file_path: str):
    import json

    with open(file_path) as json_data:
        data = json.load(json_data)
        return data
