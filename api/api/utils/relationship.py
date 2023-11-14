from api.models.enums import Relationship


def get_relationship(relationship: str) -> Relationship:
    if relationship == "friend":
        return Relationship.FRIEND
    if relationship == "enemy":
        return Relationship.ENEMY
    if relationship == "default":
        return Relationship.DEFAULT
    raise ValueError(f"Relationship {relationship} is not a valid relationship")


def get_relationship_str(relationship: Relationship) -> str:
    if relationship == Relationship.FRIEND:
        return "friend"
    if relationship == Relationship.ENEMY:
        return "enemy"
    if relationship == Relationship.DEFAULT:
        return "default"
    raise ValueError(f"Relationship {relationship} is not a valid relationship")
