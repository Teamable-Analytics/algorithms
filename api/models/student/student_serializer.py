import json

from api.models.student.student import Student


class StudentSerializer(json.JSONEncoder, json.JSONDecoder):
    def default(self, student):
        print(type(student))
        if not isinstance(student, Student):
            raise TypeError("Object is not a student instance.")
        return {
            "_id": student._id,
            "name": student.name,
            "attributes": student.attributes,
            "relationships": {f"{x}": y.value for x, y in student.relationships.items()},
            "project_preferences": student.project_preferences
        }
