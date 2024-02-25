from json import JSONEncoder
from typing import Dict, Union, List, Any

from api.models.enums import Relationship
from api.models.interfaces import ModelDecoder
from api.models.student import Student
from api.api.utils.relationship import get_relationship


class StudentSerializer(JSONEncoder, ModelDecoder):
    def default(
        self, student: Student
    ) -> Dict[
        str, Union[str, List[int], Dict[int, Relationship], Dict[int, List[int]], int]
    ]:
        if not isinstance(student, Student):
            raise TypeError("Object is not a student instance.")
        return_student_json = {
            "id": student.id,
            "name": student.name,
            "attributes": student.attributes,
            "relationships": {
                str(x): y.value for x, y in student.relationships.items()
            },
            "project_preferences": student.project_preferences,
        }
        if student.name is None:
            del return_student_json["name"]

        return return_student_json

    def decode(self, json_dict: Dict[str, Any]) -> Student:
        return Student(
            _id=int(json_dict.get("id", json_dict.get("_id"))),
            name=json_dict.get("name"),
            attributes={
                int(key): value for key, value in json_dict["attributes"].items()
            },
            relationships={
                int(key): Relationship(value)
                if isinstance(value, float) or isinstance(value, int)
                else get_relationship(value)
                for key, value in json_dict["relationships"].items()
            },
            project_preferences=json_dict.get("project_preferences"),
        )
