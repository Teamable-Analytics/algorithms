from api.models.enums import ScenarioAttribute, Gender, YearLevel
from benchmarking.data.real_data.cosc341_w2021_t2_provider.providers import (
    COSC341W2021T2StudentProvider,
)

# Number of grad students = 7
students = COSC341W2021T2StudentProvider().get()
print(len(students))
grad_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.YEAR_LEVEL.value][0]
    == YearLevel.Graduate.value
]
print(f"Number of grad students: {len(grad_students)}")

# Number of undergrad students
undergrad_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.YEAR_LEVEL.value][0]
    == YearLevel.Third.value
]
print(f"Number of undergraduate students: {len(undergrad_students)}")

# Number of male students
male_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.GENDER.value][0] == Gender.MALE.value
]
print(f"Number of male students: {len(male_students)}")

# Number of Female students
female_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.GENDER.value][0] == Gender.FEMALE.value
]
print(f"Number of Female students: {len(female_students)}")

# Number of Non-Binary students
non_binary_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.GENDER.value][0] == Gender.NON_BINARY.value
]
print(f"Number of Non-Binary students: {len(non_binary_students)}")

# Number of Other students
other_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.GENDER.value][0] == Gender.OTHER.value
]
print(f"Number of Other students: {len(other_students)}")

# Number of Prefer not to say students
no_answer_students = [
    student
    for student in students
    if student.attributes[ScenarioAttribute.GENDER.value][0] == Gender.NA.value
    or len(student.attributes[ScenarioAttribute.GENDER.value]) == 0
]
print(f"Number of Prefer Not to Answer students: {len(no_answer_students)}")

print("Time Slot Stats:")

timeslot_1 = [
    student
    for student in students
    if 1 in student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
]

print(f"Number of Timeslot 1 Students: {len(timeslot_1)}")

timeslot_2 = [
    student
    for student in students
    if 2 in student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
]

print(f"Number of Timeslot 2 Students: {len(timeslot_2)}")

timeslot_3 = [
    student
    for student in students
    if 3 in student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
]

print(f"Number of Timeslot 3 Students: {len(timeslot_3)}")

timeslot_4 = [
    student
    for student in students
    if 4 in student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
]

print(f"Number of Timeslot 4 Students: {len(timeslot_4)}")

timeslot_5 = [
    student
    for student in students
    if 5 in student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
]

print(f"Number of Timeslot 5 Students: {len(timeslot_5)}")

timeslot_6 = [
    student
    for student in students
    if 6 in student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]
]

print(f"Number of Timeslot 6 Students: {len(timeslot_6)}")

# i = 0
# for student in students:
#     i += 1
#     print(
#         f"Timeslot: {student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]}"
#     )
#
# print(i)
