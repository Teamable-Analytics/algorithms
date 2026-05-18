# runs/

A format-agnostic CLI for running team formation algorithms on CSV data.

## Structure

```
runs/
├── cli.py                   # CLI entry point
└── {format_name}/           # One directory per CSV format
    ├── input.csv            # Place your CSV here
    ├── params.json          # Algorithm configuration
    └── transform.py         # CSV → Student transformation (Claude writes this)
```

## Usage

```bash
# Output teams to stdout
python -m runs.cli {format_name}

# Output teams to a file
python -m runs.cli {format_name} --output teams.json
```

## Adding a new CSV format

1. Create `runs/{format_name}/`
2. Drop your CSV in as `runs/{format_name}/input.csv`
3. Copy `params.json` from an existing format and adjust as needed
4. Ask Claude to write `transform.py` — provide your CSV headers and what each column means

## transform.py contract

Every `transform.py` must implement exactly this function:

```python
from typing import List
from algorithms.dataclasses.student import Student

def get_students(csv_path: str) -> List[Student]:
    ...
```

- `csv_path` — absolute path to `input.csv`
- Returns a list of fully constructed `Student` objects

## params.json schema

```json
{
  "algorithm_type": "social | weight | priority | random",
  "team_generation": {
    "max_team_size": 5,
    "min_team_size": 2,
    "total_teams": "auto"
  },
  "algorithm_options": {
    "max_project_preferences": 0,
    "social_weight": 0,
    "diversity_weight": 0,
    "requirement_weight": 0,
    "preference_weight": 0,
    "friend_behaviour": "enforce | ignore | invert",
    "enemy_behaviour": "enforce | ignore | invert",
    "attributes_to_diversify": [],
    "attributes_to_concentrate": []
  },
  "algorithm_config": {
    "MAX_KEEP": 15,
    "MAX_SPREAD": 30,
    "MAX_ITERATE": 30,
    "MAX_TIME": 30
  }
}
```

**Notes:**
- `total_teams: "auto"` computes team count as `ceil(num_students / max_team_size)`
- `algorithm_config` is optional (omit to use defaults); only meaningful for `priority`
- `algorithm_options` can be omitted entirely for `random`
- Priority algorithm also accepts a `priorities` list under `algorithm_options`

## Output format

```json
{
  "id": null,
  "name": null,
  "teams": [
    {
      "id": 1,
      "name": null,
      "project_id": null,
      "requirements": [],
      "students": [
        {
          "id": 123456789,
          "name": "First Last",
          "attributes": {},
          "relationships": {"987654321": "friend"},
          "project_preferences": []
        }
      ]
    }
  ]
}
```
