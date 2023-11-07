from api.models.enums import Relationship


def get_relationship(relationship: str) -> Relationship:
    if relationship == "friend":
        return Relationship.FRIEND
    if relationship == "enemy":
        return Relationship.ENEMY
    if relationship == "default":
        return Relationship.DEFAULT
    raise ValueError(f"Relationship {relationship} is not a valid relationship")
