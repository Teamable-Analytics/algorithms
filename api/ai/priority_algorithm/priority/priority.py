from dataclasses import dataclass
from typing import List, Optional, Dict

from schema import And, Or, Schema, Optional as SchemaOptional

from api.ai.priority_algorithm.priority.interfaces import Priority
from api.ai.priority_algorithm.priority.utils import (
    infer_possible_values,
    int_dot_product,
    student_attribute_binary_vector,
)
from api.ai.weight_algorithm.utility.diversity_utility import _blau_index
from api.dataclasses.enums import (
    DiversifyType,
    TokenizationConstraintDirection,
    RequirementsCriteria,
    PriorityType,
    Relationship,
)
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from benchmarking.evaluations.enums import PreferenceDirection
from utils.math import change_range


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
        """
        The score here is intended to reflect the following cases:

            1. Diversification with min k of x (team size is T)
                - If num_tokenized_students == k | score == 1
                - If 0 < num_tokenized_students < k | score == 0
                - If num_tokenized_students == 0 | score == ?
                    + score would be equivalent to as if num_tokenized_students == T
                - If num_tokenized_students > k | score == ?
                    + score should DECREASE as num_tokenized_students INCREASES:
                    i.e. score(num_tokenized_students == k + 1) >> score(num_tokenized_students == T)

            2. Concentration with max k of x (team size is T)
                - If num_tokenized_students == k | score == 1
                - If k < num_tokenized_students < T | score == 0
                - If num_tokenized_students == 0 | score == ?
                    + score would be equivalent to as if num_tokenized_students == 1
                - If num_tokenized_students < k | score == ?
                    + score should DECREASE as num_tokenized_students DECREASES:
                    i.e. score(num_tokenized_students == k - 1) >> score(num_tokenized_students == 1)
        """
        tokenized_student_count = 0
        _THETA = 0.2

        for student in students:
            tokenized_student_count += self.value in student.attributes.get(
                self.attribute_id, []
            )
        meets_threshold = self.student_count_meets_threshold(tokenized_student_count)

        if not meets_threshold:
            return 0

        if tokenized_student_count == self.threshold:
            return 1

        team_size = len(students)
        if self.strategy == DiversifyType.DIVERSIFY:
            if tokenized_student_count == 0 or tokenized_student_count == team_size:
                return _THETA
            return ((2 * _THETA - 1) / (team_size - self.threshold - 1)) * (
                tokenized_student_count - team_size
            ) + _THETA

        if self.strategy == DiversifyType.CONCENTRATE:
            if tokenized_student_count == 0 or tokenized_student_count == 1:
                return _THETA
            return ((1 - 2 * _THETA) / (self.threshold - 2)) * (
                tokenized_student_count - 1
            ) + _THETA

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

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "attribute_id": int,
                "strategy": And(
                    str, Or(*[strategy.value for strategy in DiversifyType])
                ),
                "direction": And(
                    str,
                    Or(
                        *[
                            direction.value
                            for direction in TokenizationConstraintDirection
                        ]
                    ),
                ),
                "threshold": int,
                "value": int,
            }
        )

    @staticmethod
    def parse_json(data: Dict) -> "TokenizationPriority":
        return TokenizationPriority(
            attribute_id=data["attribute_id"],
            strategy=DiversifyType(data["strategy"]),
            direction=TokenizationConstraintDirection(data["direction"]),
            threshold=data["threshold"],
            value=data["value"],
        )


@dataclass
class DiversityPriority(Priority):
    attribute_id: int
    strategy: DiversifyType
    # the max number of values a student can have for the attribute_id
    max_num_choices: Optional[int] = None

    def validate(self):
        super().validate()
        if self.strategy == DiversifyType.CONCENTRATE and not self.max_num_choices:
            raise ValueError(
                "max_num_choices must be specified with strategy == CONCENTRATE and cannot be 0."
            )

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        if self.strategy == DiversifyType.CONCENTRATE:
            if len(students) == 0:
                return 0

            possible_attribute_values = infer_possible_values(
                students, self.attribute_id
            )
            dot_products = []  # will have length of (num students)choose(2)
            for student_i in students:
                for student_j in students:
                    if student_i.id == student_j.id:
                        break
                    dot_product = int_dot_product(
                        student_attribute_binary_vector(
                            student_i, self.attribute_id, possible_attribute_values
                        ),
                        student_attribute_binary_vector(
                            student_j, self.attribute_id, possible_attribute_values
                        ),
                    )
                    dot_products.append(dot_product)

            if len(dot_products) == 0:
                return 0

            return sum(dot_products) / (len(dot_products) * self.max_num_choices)

        if self.strategy == DiversifyType.DIVERSIFY:
            return _blau_index(students, self.attribute_id)

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "attribute_id": int,
                "strategy": And(
                    str, Or(*[strategy.value for strategy in DiversifyType])
                ),
                SchemaOptional("max_num_choices"): int,
            }
        )

    @staticmethod
    def parse_json(data: Dict) -> "DiversityPriority":
        return DiversityPriority(
            attribute_id=data["attribute_id"],
            strategy=DiversifyType(data["strategy"]),
            max_num_choices=data.get("max_num_choices"),
        )


@dataclass
class RequirementPriority(Priority):
    def validate(self):
        super().validate()

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        num_team_requirements = len(team_shell.requirements)
        if num_team_requirements <= 0:
            # If a team has no requirements then the student is a perfect match
            return 1

        total_requirement_satisfaction = 0
        for req in team_shell.requirements:
            total_requirement_satisfaction += req.satisfaction_by_students(students)

        return total_requirement_satisfaction / num_team_requirements

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "criteria": And(
                    str, Or(*[criteria.value for criteria in RequirementsCriteria])
                ),
            }
        )

    @staticmethod
    def parse_json(data: Dict) -> "RequirementPriority":
        return RequirementPriority()


@dataclass
class ProjectPreferencePriority(Priority):
    direction: PreferenceDirection
    max_project_preferences: int

    def validate(self):
        super().validate()

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        max_satisfaction_score = len(students) * self.max_project_preferences
        satisfaction_score = 0
        for student in students:
            for index, preference in enumerate(student.project_preferences):
                if preference == team_shell.project_id:
                    satisfaction_score += self.max_project_preferences - index

        if self.direction == PreferenceDirection.EXCLUDE:
            return (
                max_satisfaction_score - satisfaction_score
            ) / max_satisfaction_score
        return satisfaction_score / max_satisfaction_score

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "direction": And(
                    str, Or(*[direction.value for direction in PreferenceDirection])
                ),
                "max_project_preferences": int,
            }
        )

    @staticmethod
    def parse_json(data: Dict) -> "ProjectPreferencePriority":
        return ProjectPreferencePriority(
            direction=PreferenceDirection(data["direction"]),
            max_project_preferences=data["max_project_preferences"],
        )


@dataclass
class SocialPreferencePriority(Priority):
    max_num_friends: int
    max_num_enemies: int

    def validate(self):
        super().validate()

    def satisfaction(self, students: List[Student], team_shell: TeamShell) -> float:
        num_students = len(students)
        student_ids = [s.id for s in students]
        # bidirectional friendship for all team members
        theoretical_min = (
            num_students * self.max_num_friends * Relationship.FRIEND.value
        )
        # bidirectional enemies for all team members
        theoretical_max = num_students * self.max_num_enemies * Relationship.ENEMY.value

        total = 0
        for student in students:
            for relation_student_id, relationship in student.relationships.items():
                if (
                    relation_student_id in student_ids
                    and relation_student_id != student.id
                ):
                    total += relationship.value

        # subtract the total from 1 because FRIEND is a negative number, meaning the closer we are to the theoretical
        # min, the better for social satisfaction
        return 1 - change_range(
            total, original_range=(theoretical_min, theoretical_max), new_range=(0, 1)
        )

    @staticmethod
    def get_schema() -> Schema:
        return Schema(
            {
                "max_num_friends": int,
                "max_num_enemies": int,
            }
        )

    @staticmethod
    def parse_json(data: Dict) -> "SocialPreferencePriority":
        return SocialPreferencePriority(
            max_num_friends=data["max_num_friends"],
            max_num_enemies=data["max_num_enemies"]
        )


def get_priority_from_type(priority_type: PriorityType):
    if priority_type == PriorityType.TOKENIZATION:
        return TokenizationPriority
    if priority_type == PriorityType.DIVERSITY:
        return DiversityPriority
    if priority_type == PriorityType.PROJECT_REQUIREMENT:
        return RequirementPriority
    if priority_type == PriorityType.PROJECT_PREFERENCE:
        return ProjectPreferencePriority
    if priority_type == PriorityType.SOCIAL_PREFERENCE:
        return SocialPreferencePriority
    raise NotImplementedError()
