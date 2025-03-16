from dataclasses import dataclass

from algorithms.dataclasses.enums import TokenizationConstraintDirection


@dataclass
class TokenizationConstraint:
    direction: TokenizationConstraintDirection
    threshold: int
    value: int
