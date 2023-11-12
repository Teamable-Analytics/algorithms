import unittest

from api.ai.interfaces.algorithm import Algorithm
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.models.team import TeamShell
from utils.validation import is_unique


class TestAlgorithm(unittest.TestCase):
    def test_create_initial_teams__creates_teams_with_unique_ideas(self):
        # without initial teams
        team_generation_options_1 = TeamGenerationOptions(
            max_team_size=5, min_team_size=4, total_teams=4, initial_teams=[]
        )
        teams_1 = Algorithm.create_initial_teams(team_generation_options_1)
        self.assertTrue(is_unique([t.id for t in teams_1]))
        self.assertTrue(is_unique([t.name for t in teams_1]))

        # with initial teams
        team_generation_options_2 = TeamGenerationOptions(
            max_team_size=5,
            min_team_size=4,
            total_teams=4,
            initial_teams=[
                TeamShell(_id=2),
                TeamShell(_id=20),
            ],
        )
        teams_2 = Algorithm.create_initial_teams(team_generation_options_2)
        teams_2_ids = [t.id for t in teams_2]
        self.assertTrue(is_unique(teams_2_ids))
        self.assertTrue(is_unique([t.name for t in teams_2]))
        # the 2 new teams created to reach total_teams should have these 2 ids specifically
        self.assertTrue(21 in teams_2_ids)
        self.assertTrue(22 in teams_2_ids)

        # with initial teams with names that will clash
        team_generation_options_3 = TeamGenerationOptions(
            max_team_size=5,
            min_team_size=4,
            total_teams=4,
            initial_teams=[
                TeamShell(_id=2, name="Team 21"),
                TeamShell(_id=20, name="Team 22"),
            ],
        )
        teams_3 = Algorithm.create_initial_teams(team_generation_options_3)
        teams_3_ids = [t.id for t in teams_3]
        self.assertTrue(is_unique(teams_3_ids))
        self.assertTrue(is_unique([t.name for t in teams_3]))
        # the 2 new teams created to reach total_teams should have these 2 ids specifically
        self.assertTrue(23 in teams_3_ids)
        self.assertTrue(24 in teams_3_ids)
