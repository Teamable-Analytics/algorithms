import json
import string

from api.models.enums import Relationship
from api.models.student.student import Student


class StudentSerializer(json.JSONEncoder, json.JSONDecoder):
    def default(self, student: Student) -> string:
        if not isinstance(student, Student):
            raise TypeError("Object is not a student instance.")
        return {
            "_id": student._id,
            "name": student.name,
            "attributes": student.attributes,
            "relationships": {
                f"{x}": y.value for x, y in student.relationships.items()
            },
            "project_preferences": student.project_preferences,
        }

    def decode(self, s, _w=...) -> Student:
        data = json.loads(s)
        return Student(
            _id=data["_id"],
            name=data["name"],
            attributes={int(key): value for key, value in data["attributes"].items()},
            relationships={
                int(key): Relationship(value)
                for key, value in data["relationships"].items()
            },
            project_preferences=data["project_preferences"],
        )
