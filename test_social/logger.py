from algorithm.consts import FRIEND
from student import Student
from team import Team
from test_social.mock_team_generation import KEY_FILE_PATH, load_json_data


class Logger:
    real = False

    def __init__(self, real: bool = False):
        self.real = real

    def print_teams(self, teams: [Team]):
        print(f'Number of teams: {len(teams)}')
        for team in teams:
            print(f'Team: {team.id}')
            for student in team.students:
                info = student.id
                if self.real:
                    info = get_student_from_key(student)
                print(f'\tStudent - {info}')


def get_student_from_key(student_anon: Student):
    student_key = load_json_data(KEY_FILE_PATH)
    student_name = get_student_name(student_key, student_anon.id)
    friends = [get_student_name(student_key, other_id)
               for other_id, relationship
               in student_anon.relationships.items()
               if relationship == FRIEND]

    return f'{student_name} => Friends ({", ".join(friends)})'


def get_student_name(student_key: dict, student_anon_id: int) -> str:
    for real_id, student_info in student_key.items():
        if student_info['anon_student_id'] == student_anon_id:
            return student_info['real_name']
    return f'Unknown Student ({student_anon_id})'
