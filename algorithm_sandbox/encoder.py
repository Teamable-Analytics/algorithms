from typing import Dict

from team_formation.app.team_generator.student import Student


# Currently hardcoded, these file paths must be from the root directory and lead to the mock data .json files being
# used.

# Both files are the output from running 'serialize_group_set <canvas_course_id> <gen_group_set_id>' in the main
# website's Django terminal. The format can be found in the GroupDataRetrieval class in the main repo, too.
DATA_FILE_PATH = "algorithm_sandbox/mock_data/gen_group_set-20220331_141058.json"
KEY_FILE_PATH = "algorithm_sandbox/mock_data/student_key-20220331_141058.json"


class Encoder:
    """
    Responsible for converting anonymized data in mock files into real student names for validation and logging purposes
    """
    STUDENT_KEY_CACHE = None

    @staticmethod
    def get_student_name(student: Student) -> str:
        student_key = load_json_data(KEY_FILE_PATH)
        student_name = Encoder.get_student_name_by_id(student_key, student.id)
        return student_name

    @staticmethod
    def get_student_name_by_id(student_key: dict, student_anon_id: int) -> str:
        """
        Finds a student's real name given their anonymized id.
        'No Name (<ID>)' refers to a registered student who's name is null in the database.
        'Unregistered' refers to an unregistered student
        """
        for real_id, student_info in student_key.items():
            if student_info['anon_student_id'] == student_anon_id:
                student_name = student_info['real_name']
                return student_name if student_name else f'No Name ({real_id})'
        return f'Unregistered'

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
