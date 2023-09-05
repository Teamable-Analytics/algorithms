import random

from old.team_formation.app.team_generator.algorithm.algorithms import AlgorithmOptions
from old.team_formation.app.team_generator.team import Team
from old.team_formation.app.team_generator.algorithm.consts import REQUIREMENT_TYPES

priorities = []

algorithm_options = AlgorithmOptions(
    diversity_weight=0,
    social_weight=0,
    preference_weight=1,
    requirement_weight=1,
    whitelist_behaviour="ignore",
    blacklist_behaviour="ignore",
)


def s3_options(num_team, num_req, req_per_project):
    requirements = [
        {
            "id": i + 10,
            "operator": REQUIREMENT_TYPES.EXACTLY,
            "value": 1,
        }
        for i in range(num_req)
    ]

    teams = [
        Team(
            id=str(i),
            project_id=i,
            name=str(i),
            requirements=random.sample(requirements, k=req_per_project),
        )
        for i in range(num_team)
    ]
    return priorities, algorithm_options, teams
