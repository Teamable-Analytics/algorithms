def get_diversity_utility(team, student, diversify_options, concentrate_options):
    if not diversify_options and not concentrate_options:
        return 0

    temp_team_students = [s for s in team.students]
    temp_team_students.append(student)

    max_value_possible = len(diversify_options) + len(concentrate_options)
    min_value_possible = -max_value_possible

    value = 0
    for diversify_option in diversify_options:
        bi_old = _blau_index(team.students, diversify_option["id"])
        bi_new = _blau_index(temp_team_students, diversify_option["id"])
        value += bi_new - bi_old
    for concentrate_option in concentrate_options:
        bi_old = 1 - _blau_index(team.students, concentrate_option["id"])
        bi_new = 1 - _blau_index(temp_team_students, concentrate_option["id"])
        value += bi_new - bi_old

    # Normalize value to the range of [0, 1], then scale it
    normalized_value = (value - min_value_possible) / (2 * max_value_possible)

    scaled_value = _scale_diversity_utility(normalized_value)
    return scaled_value


def _scale_diversity_utility(value):
    return value ** (1 / 3)


def _blau_index(students, skill_id):
    # NOTE: A non-answer (i.e. answer=[-1]) counts as an answer option here
    # a tally of each answer encountered and it's frequency
    answer_frequencies = _get_answer_frequencies(students, skill_id)

    cumulative_sum = 0
    total = len(students)
    for frequency in answer_frequencies.values():
        cumulative_sum += (frequency / total) ** 2
    return 1 - cumulative_sum


def _get_answer_frequencies(students, skill_id):
    answer_frequencies = {}
    for student in students:
        if skill_id in student.skills:
            answer_set = student.get_skill(skill_id)
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
