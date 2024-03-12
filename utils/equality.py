from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.dataclasses.student import Student
    from api.dataclasses.team import Team


def are_students_equal_ignoring_team(s1: "Student", s2: "Student"):
    from api.dataclasses.student import Student

    for field_name in Student.__dataclass_fields__.keys():
        if field_name == "team":
            continue
        if s1.__getattribute__(field_name) != s2.__getattribute__(field_name):
            return False
    return True


def are_teams_equal_ignoring_students(t1: "Team", t2: "Team"):
    from api.dataclasses.team import Team

    for field_name in Team.__dataclass_fields__.keys():
        if field_name == "students":
            continue
        if t1.__getattribute__(field_name) != t2.__getattribute__(field_name):
            return False
    return True


def teams_are_equal(t1: "Team", t2: "Team") -> bool:
    if id(t1) == id(t2):  # literally the same memory address
        return True

    # soft equality to avoid recursion depth error
    if str(t1) != str(t2):
        return False

    if len(t1.students) != len(t2.students):
        return False

    if not are_teams_equal_ignoring_students(t1, t2):
        return False

    # a delicate approach to checking for deeper equality without causing the recursion depth error
    for s1, s2 in zip(
        sorted(t1.students, key=lambda s: s.id), sorted(t2.students, key=lambda s: s.id)
    ):
        if not are_students_equal_ignoring_team(s1, s2):
            return False
        if not are_teams_equal_ignoring_students(s1.team, s2.team):
            return False

    return True
