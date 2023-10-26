from json import JSONEncoder
from typing import Dict, Union, List, Any

from api.models.enums import Relationship
from api.models.interfaces import ModelDecoder
from api.models.student import Student


class StudentSerializer(JSONEncoder, ModelDecoder):
    def default(
        self, student: Student
    ) -> Dict[
        str, Union[str, List[int], Dict[int, Relationship], Dict[int, List[int]], int]
    ]:
        if not isinstance(student, Student):
            raise TypeError("Object is not a student instance.")
        return {
            "_id": student._id,
            "name": student.name,
            "attributes": student.attributes,
            "relationships": {
                str(x): y.value for x, y in student.relationships.items()
            },
            "project_preferences": student.project_preferences,
        }

    def decode(self, json_dict: Dict[str, Any]) -> Student:
        return Student(
            _id=json_dict["_id"],
            name=json_dict["name"],
            attributes={
                int(key): value for key, value in json_dict["attributes"].items()
            },
            relationships={
                int(key): Relationship(value)
                for key, value in json_dict["relationships"].items()
            },
            project_preferences=json_dict["project_preferences"],
        )
