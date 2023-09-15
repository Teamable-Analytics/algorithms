from dataclasses import dataclass
from typing import List

from ai.priority_algorithm.interfaces import Priority
from models.enums import DiversifyType, TokenizationConstraintDirection
from models.student import Student


@dataclass
class TokenizationPriority(Priority):
    attribute_id: int
    strategy: DiversifyType
    direction: TokenizationConstraintDirection
    threshold: int  # number representing k
    value: str  # string representing x

    def __post_init__(self, *args, **kwargs):
        self.validate()

    def validate(self):
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
