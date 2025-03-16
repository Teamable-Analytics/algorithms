from enum import Enum


class Relationship(Enum):
    FRIEND = -1
    DEFAULT = 0
    ENEMY = 1.1


class RelationshipBehaviour(Enum):
    ENFORCE = "enforce"
    INVERT = "invert"
    IGNORE = "ignore"


class RequirementOperator(Enum):
    EXACTLY = "exactly"
    LESS_THAN = "less than"
    MORE_THAN = "more than"


class DiversifyType(Enum):
    DIVERSIFY = "diversify"
    CONCENTRATE = "concentrate"


class Weight(Enum):
    HIGH_WEIGHT = 10
    LOW_WEIGHT = 1


class AlgorithmType(Enum):
    RANDOM = "random"
    WEIGHT = "weight"
    SOCIAL = "social"
    PRIORITY = "priority"


class TokenizationConstraintDirection(Enum):
    MIN_OF = "min_of"
    MAX_OF = "max_of"


# todo: rename to RequirementCriteria
class RequirementsCriteria(Enum):
    EVERYONE = "everyone_meets_requirement"
    N_MEMBERS = "some_number_of_members_meet_requirement"
    SOMEONE = "someone_meets_requirement"


class PriorityType(Enum):
    TOKENIZATION = "tokenization"
    DIVERSITY = "diversity"
    PROJECT_PREFERENCE = "project_preference"
    PROJECT_REQUIREMENT = "project_requirement"
    SOCIAL_PREFERENCE = "social_preference"


class PreferenceDirection(Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"


class PreferenceSubject(Enum):
    FRIENDS = "friends"
    ENEMIES = "enemies"
    PROJECTS = "projects"
