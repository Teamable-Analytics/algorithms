import csv
import hashlib
from typing import Dict, List, Set

from algorithms.dataclasses.enums import Relationship
from algorithms.dataclasses.student import Student


def _make_id(first: str, last: str) -> int:
    key = (first + last).replace(" ", "")
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (10**9)


def _parse_names(field: str) -> Set[str]:
    """Parse 'part 1: FirstName LastName; part 2: ...' into a set of unique full names."""
    names = set()
    for part in field.split(";"):
        if ":" in part:
            name_str = part.split(":", 1)[1].strip()
            if name_str:
                names.add(name_str)
    return names


def get_students(csv_path: str) -> List[Student]:
    rows = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    name_to_id: Dict[str, int] = {
        f"{row['First_name']} {row['Last_name']}": _make_id(row["First_name"], row["Last_name"])
        for row in rows
    }

    students = []
    for row in rows:
        first, last = row["First_name"], row["Last_name"]
        sid = _make_id(first, last)
        full_name = f"{first} {last}"

        relationships: Dict[int, Relationship] = {}

        for name in _parse_names(row.get("whitelist", "")):
            if name in name_to_id and name_to_id[name] != sid:
                relationships[name_to_id[name]] = Relationship.FRIEND

        for name in _parse_names(row.get("blacklist", "")):
            if name in name_to_id and name_to_id[name] != sid:
                relationships[name_to_id[name]] = Relationship.ENEMY

        students.append(
            Student(
                _id=sid,
                name=full_name,
                attributes={},
                relationships=relationships,
                project_preferences=[],
            )
        )

    return students
