from typing import List

from old.team_formation.app.team_generator.student import Student


class PriorityException(Exception):
    pass


class Priority:
    # Constraints
    TYPE_DIVERSIFY = 'diversify'
    TYPE_CONCENTRATE = 'concentrate'
    TYPE_IGNORE = 'ignore'

    # Limit options
    MIN_OF = 'min_of'
    MAX_OF = 'max_of'

    skill_id: int
    limit_option: str
    constraint: str
    limit: int  # number representing k
    value: str  # string representing x

    def __init__(self, constraint: str, skill_id: int, limit_option: str, limit: int, value: str):
        self.constraint = constraint
        self.skill_id = skill_id
        self.limit_option = limit_option
        self.limit = limit
        self.value = value
        self.validate()

    def validate(self):
        if self.limit_option == Priority.MIN_OF and self.constraint == Priority.TYPE_DIVERSIFY:
            return True
        if self.limit_option == Priority.MAX_OF and self.constraint == Priority.TYPE_CONCENTRATE:
            if self.limit > 0:
                return True
            raise ValueError('Limit must be greater than 0')
        raise NotImplementedError()

    def satisfied_by(self, students: List[Student]) -> bool:
        count = 0
        for student in students:
            if self.skill_id in student.skills:
                count += self.value in student.skills[self.skill_id]
        return self.student_count_meets_limit(count)

    def student_count_meets_limit(self, count: int) -> bool:
        """
        @param count: The number of students in a team that have self.value in their student.skills[self.skill_id]
        @return:
        """
        if count == 0:
            return True
        if self.limit_option == Priority.MIN_OF and self.constraint == Priority.TYPE_DIVERSIFY:
            return count >= self.limit
        if self.limit_option == Priority.MAX_OF and self.constraint == Priority.TYPE_CONCENTRATE:
            return count <= self.limit
