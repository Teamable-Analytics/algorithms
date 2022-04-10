from team_formation.app.team_generator.student import Student

DATA_FILE_PATH = "algorithm_sandbox/mock_data/gen_group_set-20220331_141058.json"
KEY_FILE_PATH = "algorithm_sandbox/mock_data/student_key-20220331_141058.json"


class Encoder:
    STUDENT_KEY_CACHE = None

    @staticmethod
    def get_student_name(student_anon: Student) -> str:
        student_key = load_json_data(KEY_FILE_PATH)
        student_name = Encoder.get_student_name_by_id(student_key, student_anon.id)
        return student_name

    @staticmethod
    def get_student_name_by_id(student_key: dict, student_anon_id: int) -> str:
        for real_id, student_info in student_key.items():
            if student_info['anon_student_id'] == student_anon_id:
                student_name = student_info['real_name']
                return student_name if student_name else f'No Name ({real_id})'
        return f'Unknown Student ({student_anon_id})'

    @staticmethod
    def get_student_key():
        if Encoder.STUDENT_KEY_CACHE:
            return Encoder.STUDENT_KEY_CACHE
        student_key = load_json_data(KEY_FILE_PATH)
        Encoder.STUDENT_KEY_CACHE = student_key
        return student_key


def load_json_data(file_path: str) -> Dict:
    """
    A helper method to convert .json file paths into python dictionaries
    """
    if not file_path.endswith('.json'):
        raise Exception('File path does not end with .json, so it cannot be loaded as such.')

    import json
    with open(file_path) as json_data:
        data = json.load(json_data)
        return data
