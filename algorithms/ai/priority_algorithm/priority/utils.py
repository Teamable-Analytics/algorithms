from typing import List

from algorithms.dataclasses.student import Student


def student_attribute_binary_vector(
    student: Student, attribute_id: int, possible_values: List[int]
) -> List[int]:
    """
    Returns a list in the form [0, 1, 1, 0, ...]

    e.g. So if Student S, on Attribute A:
        - Assume A has possible values [red, blue, green, yellow]
        - Assume S has values for A [red, yellow]
        => the vector would be [1, 0, 0, 1]
    """
    if attribute_id not in student.attributes.keys():
        raise ValueError(f"Student does not have attribute with id {attribute_id}")

    return [int(p_v in student.attributes.get(attribute_id)) for p_v in possible_values]


def int_dot_product(a: List[int], b: List[int]) -> int:
    if len(a) != len(b):
        raise ValueError("The lengths of both vectors must be equal.")

    if len(a) == 0:
        return 0

    return sum(a_i * b_i for a_i, b_i in zip(a, b))


def infer_possible_values(students: List[Student], attribute_id: int) -> List[int]:
    possible_values = set()
    for s in students:
        if attribute_id not in s.attributes.keys():
            raise ValueError(f"Student does not have attribute with id {attribute_id}")

        for value in s.attributes.get(attribute_id):
            possible_values.add(value)

    return list(possible_values)
