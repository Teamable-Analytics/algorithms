from dataclasses import dataclass

from api.dataclasses.enums import TokenizationConstraintDirection


@dataclass
class TokenizationConstraint:
    direction: TokenizationConstraintDirection
    threshold: int
    value: int
