from dataclasses import dataclass
from typing import List

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.weight_algorithm.utility.diversity_utility import _blau_index
from api.models.enums import DiversifyType, TokenizationConstraintDirection
from api.models.student import Student


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

    def satisfaction(self, students: List[Student]) -> float:
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

    def satisfaction(self, students: List[Student]) -> float:
        blau_index = _blau_index(students, self.attribute_id)
        return (
            blau_index if self.strategy == DiversifyType.DIVERSIFY else (1 - blau_index)
        )
