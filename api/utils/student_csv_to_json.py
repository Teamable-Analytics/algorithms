import csv
import json
from typing import Tuple, List, Dict

from api.dataclasses.enums import Relationship
from api.dataclasses.student import Student, StudentSerializer


def _get_attribute_by_name(
    name: str, attributes: List[Tuple[int, str, Dict[str, int]]]
) -> Tuple[int, str, Dict[str, int]]:
    for attr in attributes:
        if attr[1] == name:
            return attr


def student_csv_to_json(csv_file_name: str) -> str:
    """
    Converts a CSV list of students with attributes to a JSON object compatible with the algorithms API.

    Format:
    - There are three special column names, 'student_name', 'friends', and 'enemies'. These must be spelled exactly as provided to be recognized. student_names is a required column.
    - Any other column is considered an attribute and will be numbered in the order of appearance in the output json.
    - Values for an attribute are kept as a number if it is provided as a number in the csv, otherwise a number is assigned to each unique non-integer value.
    """
    with open(csv_file_name, "r") as f:
        csv_reader = csv.reader(f)

        rows = [row for row in csv_reader]

        try:
            names_column = rows[0].index("student_name")
        except ValueError:
            raise ValueError('A "student_names" column must be supplied in the CSV')
        try:
            friends_column = rows[0].index("friends")
        except ValueError:
            friends_column = None
        try:
            enemies_column = rows[0].index("enemies")
        except ValueError:
            enemies_column = None
        known_columns = [names_column, friends_column, enemies_column]

        # Index attributes
        attributes: List[Tuple[int, str, Dict[str, int]]] = []
        for i in range(len(rows[0])):
            if i not in known_columns:
                # Map of str value as seen in csv, to int value that algo requires
                values: Dict[str, int] = {}
                non_int_values = set()
                for row in rows[1:]:
                    if row[i] != "":
                        str_values = row[i].split(",")
                        for str_value in str_values:
                            try:
                                # Try to keep the same number value if possible
                                values[str_value] = int(str_value)
                            except ValueError:
                                non_int_values.add(str_value)
                # Reconcile non int values
                next_avail_int = 0
                for val in non_int_values:
                    while next_avail_int in values.values():
                        next_avail_int += 1
                    values[val] = next_avail_int
                attributes.append((len(attributes), rows[0][i], values))

        # Map student name to id
        student_dict: Dict[str, int] = {
            row[names_column]: i for i, row in enumerate(rows[1:])
        }

        students: List[Student] = []
        for row in rows[1:]:
            relationships = (
                {
                    student_dict[name]: Relationship.FRIEND
                    for name in row[friends_column].split(",")
                }
                if friends_column and row[friends_column] != ""
                else {}
            )
            relationships.update(
                {
                    student_dict[name]: Relationship.ENEMY
                    for name in row[enemies_column].split(",")
                }
                if enemies_column and row[enemies_column] != ""
                else {}
            )

            student_attributes = {}
            for col in range(len(row)):
                if col not in known_columns:
                    attr = _get_attribute_by_name(rows[0][col], attributes)
                    vals = [
                        attr[2][value] for value in row[col].split(",") if value != ""
                    ]
                    if len(vals) > 0:
                        student_attributes[attr[0]] = vals

            students.append(
                Student(
                    _id=student_dict[row[names_column]],
                    name=row[names_column],
                    relationships=relationships,
                    attributes=student_attributes,
                )
            )

        # Convert to a dict, so we can fix the relationship values for the API
        students_json = json.dumps(students, cls=StudentSerializer)
        students_dict = json.loads(students_json)
        for student in students_dict:
            for related_student in student["relationships"].keys():
                if (
                    student["relationships"][related_student]
                    == Relationship.FRIEND.value
                ):
                    student["relationships"][related_student] = "friend"
                elif (
                    student["relationships"][related_student]
                    == Relationship.ENEMY.value
                ):
                    student["relationships"][related_student] = "enemy"
                else:
                    student["relationships"][related_student] = "default"

        return json.dumps(students_dict, indent=4)
