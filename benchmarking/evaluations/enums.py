from enum import Enum


class PreferenceDirection(Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"


class PreferenceSubject(Enum):
    FRIENDS = "friends"
    ENEMIES = "enemies"
    PROJECTS = "projects"
