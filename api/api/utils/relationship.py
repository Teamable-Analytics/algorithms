from typing import Any

from api.models.enums import Relationship


def get_relationship(relationship: str) -> Relationship:
    if relationship == "friend":
        return Relationship.FRIEND
    if relationship == "enemy":
        return Relationship.ENEMY
    if relationship == "default":
        return Relationship.DEFAULT
    raise ValueError(f"Relationship {relationship} is not a valid relationship")


def get_relationship_value(relationship: Any) -> int:
    if isinstance(relationship, Relationship):
        return relationship.value
    if isinstance(relationship, str):
        return get_relationship(relationship).value
    if isinstance(relationship, int):
        return relationship

    raise ValueError(f"Relationship {relationship} does not have a valid type")
