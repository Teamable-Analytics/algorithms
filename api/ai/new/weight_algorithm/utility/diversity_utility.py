from typing import List, Dict

from api.models.student.student import Student
from api.models.team import Team


def get_diversity_utility(
    team: Team,
    student: Student,
    attributes_to_diversify: List[int],
    attributes_to_concentrate: List[int],
) -> float:
    if not attributes_to_diversify and not attributes_to_concentrate:
        return 0

    temp_team_students = [s for s in team.students]
    temp_team_students.append(student)

    max_value_possible = len(attributes_to_diversify) + len(attributes_to_concentrate)
    min_value_possible = -max_value_possible

    value = 0
    for diversify_attribute_id in attributes_to_diversify:
        bi_old = _blau_index(team.students, diversify_attribute_id)
        bi_new = _blau_index(temp_team_students, diversify_attribute_id)
        value += bi_new - bi_old

    for concentrate_attribute_id in attributes_to_concentrate:
        bi_old = 1 - _blau_index(team.students, concentrate_attribute_id)
        bi_new = 1 - _blau_index(temp_team_students, concentrate_attribute_id)
        value += bi_new - bi_old

    # Normalize value to the range of [0, 1], then scale it
    normalized_value = (value - min_value_possible) / (2 * max_value_possible)

    scaled_value = _scale_diversity_utility(normalized_value)
    return scaled_value


def _scale_diversity_utility(value: float) -> float:
    return value ** (1 / 3)


def _blau_index(students: List[Student], attribute_id: int) -> float:
    # NOTE: A non-answer (i.e. answer=[-1]) counts as an answer option here
    #   a tally of each answer encountered, and it's frequency
    answer_frequencies = _get_answer_frequencies(students, attribute_id)

    cumulative_sum = 0
    total = len(students)
    for frequency in answer_frequencies.values():
        cumulative_sum += (frequency / total) ** 2
    return 1 - cumulative_sum


def _get_answer_frequencies(
    students: List[Student], attribute_id: int
) -> Dict[int, int]:
    answer_frequencies = {}
    for student in students:
        if attribute_id in student.attributes:
            answer_set = student.attributes[attribute_id]
            is_multi_answer = len(answer_set) > 1
            num_answers = len(answer_set) if answer_set else 1
            for answer in answer_set:
                try:
                    answer_frequencies[answer] += (
                        1 / num_answers if is_multi_answer else 1
                    )
                except KeyError:
                    answer_frequencies[answer] = (
                        1 / num_answers if is_multi_answer else 1
                    )
    return answer_frequencies
