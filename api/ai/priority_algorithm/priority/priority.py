from dataclasses import dataclass
from typing import List

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.weight_algorithm.utility.diversity_utility import _blau_index
from api.models.enums import (
    DiversifyType,
    TokenizationConstraintDirection,
    RequirementsCriteria,
)
from api.models.student import Student
from api.models.team import TeamShell


@dataclass
class TokenizationPriority(Priority):
    attribute_id: int
    strategy: DiversifyType
    direction: TokenizationConstraintDirection
    threshold: int  # number representing k
    value: int  # string representing x

    def validate(self):
        super().validate()
        if (
            self.direction == TokenizationConstraintDirection.MIN_OF
            and self.strategy == DiversifyType.DIVERSIFY
        ):
            return True
        if (
            self.direction == TokenizationConstraintDirection.MAX_OF
            and self.strategy == DiversifyType.CONCENTRATE
        ):
            if self.threshold > 0:
                return True
            raise ValueError("Limit must be greater than 0")
        raise NotImplementedError()

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        return int(self.satisfied_by(students))

    def satisfied_by(self, students: List[Student]) -> bool:
        count = 0
        for student in students:
            count += self.value in student.attributes.get(self.attribute_id, [])
        return self.student_count_meets_threshold(count)

    def student_count_meets_threshold(self, count: int) -> bool:
        if count == 0:
            return True

        if (
            self.direction == TokenizationConstraintDirection.MIN_OF
            and self.strategy == DiversifyType.DIVERSIFY
        ):
            return count >= self.threshold
        if (
            self.direction == TokenizationConstraintDirection.MAX_OF
            and self.strategy == DiversifyType.CONCENTRATE
        ):
            return count <= self.threshold


@dataclass
class DiversityPriority(Priority):
    attribute_id: int
    strategy: DiversifyType

    def validate(self):
        super().validate()

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        blau_index = _blau_index(students, self.attribute_id)
        return (
            blau_index if self.strategy == DiversifyType.DIVERSIFY else (1 - blau_index)
        )


@dataclass
class RequirementPriority(Priority):
    criteria: RequirementsCriteria

    def validate(self):
        super().validate()

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        num_team_requirements = len(team_shell.requirements)
        if num_team_requirements <= 0:
            # If a team has no requirements then the student is a perfect match
            return 1

        if self.criteria == RequirementsCriteria.PROJECT_REQUIREMENTS_ARE_SATISFIED:
            total_met_requirements = 0
            for req in team_shell.requirements:
                for student in students:
                    if student.meets_requirement(req):
                        total_met_requirements += 1
                        break

            return total_met_requirements / num_team_requirements

        if self.criteria == RequirementsCriteria.STUDENT_ATTRIBUTES_ARE_RELEVANT:
            num_students_that_meet_any_req = sum(
                [
                    (team_shell.num_requirements_met_by_student(student) > 0)
                    for student in students
                ]
            )
            return num_students_that_meet_any_req / len(students)
