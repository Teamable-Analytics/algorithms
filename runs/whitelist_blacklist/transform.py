import csv
import hashlib
import json
import re
from typing import Dict, List, Set

from algorithms.dataclasses.enums import Relationship
from algorithms.dataclasses.student import Student


def _to_key(s: str) -> str:
    """Strip to alphanumeric only for robust name matching across export formats."""
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()


def _make_id(first: str, last: str) -> int:
    key = _to_key(first + last)
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (10**9)


def _parse_names(field: str) -> Set[str]:
    """Parse 'part 1: FirstName LastName; part 2: ...' into a set of alphanumeric keys."""
    names = set()
    for part in field.split(";"):
        if ":" in part:
            key = _to_key(part.split(":", 1)[1])
            if key:
                names.add(key)
    return names


def get_students(csv_path: str) -> List[Student]:
    rows = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    name_to_id: Dict[str, int] = {
        _to_key(f"{row['First_name']}{row['Last_name']}"): _make_id(
            row["First_name"], row["Last_name"]
        )
        for row in rows
    }

    students = []
    for row in rows:
        first, last = row["First_name"], row["Last_name"]
        sid = _make_id(first, last)
        full_name = f"{re.sub(r'[^a-zA-Z0-9]', '', first)} {re.sub(r'[^a-zA-Z0-9]', '', last)}"

        relationships: Dict[int, Relationship] = {}

        for key in _parse_names(row.get("whitelist", "")):
            if key in name_to_id and name_to_id[key] != sid:
                relationships[name_to_id[key]] = Relationship.FRIEND

        for key in _parse_names(row.get("blacklist", "")):
            if key in name_to_id and name_to_id[key] != sid:
                relationships[name_to_id[key]] = Relationship.ENEMY

        students.append(
            Student(
                _id=sid,
                name=full_name,
                attributes={},
                relationships=relationships,
                project_preferences=[],
            )
        )

    id_to_name = {s.id: s.name for s in students}
    friendship_map = {
        s.name: {
            id_to_name[other_id]: rel.name.lower()
            for other_id, rel in s.relationships.items()
        }
        for s in students
    }
    print(json.dumps(friendship_map, indent=2))

    return students
