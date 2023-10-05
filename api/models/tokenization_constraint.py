from dataclasses import dataclass

from models.enums import TokenizationConstraintDirection


@dataclass
class TokenizationConstraint:
    direction: TokenizationConstraintDirection
    threshold: int
    value: int
