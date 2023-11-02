from typing import List

from api.models.project import ProjectRequirement
from api.models.student import Student


class SupportGroup:
    def __init__(self, requirement: ProjectRequirement, students: List[Student]):
        """
        Args:
            attribute_id: The attribute id of the support group
            students: The students in the support group
        """
        self.students = students
        self.requirement = requirement
        self.value = len(students)


class Distance:
    def __init__(
        self, value: float, start_student: Student = None, end_student: Student = None
    ):
        self.value = value
        self.start_student = start_student
        self.end_student = end_student
        self.is_updated = False
