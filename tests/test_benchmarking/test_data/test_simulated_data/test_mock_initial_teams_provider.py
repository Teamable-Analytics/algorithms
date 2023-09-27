import unittest

from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    projects_to_teams,
    team_shells_to_teams,
    MockInitialTeamsProviderSettings,
)
from models.enums import RequirementOperator
from models.project import Project, ProjectRequirement
from models.team import Team, TeamShell


class TestMockInitialTeamsProvider(unittest.TestCase):
    def test_init__errors_with_duplicate_project_ids(self):
        with self.assertRaises(ValueError):
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(
                    projects=[Project(_id=1), Project(_id=1)]
                )
            )

    def test_init__errors_with_duplicate_project_names(self):
        with self.assertRaises(ValueError):
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(
                    projects=[Project(_id=1, name="A"), Project(_id=2, name="A")]
                )
            )

    def test_init__errors_with_duplicate_team_shell_ids(self):
        with self.assertRaises(ValueError):
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(
                    initial_teams=[TeamShell(_id=1), TeamShell(_id=1)]
                )
            )

    def test_init__errors_with_duplicate_team_shell_names(self):
        with self.assertRaises(ValueError):
            MockInitialTeamsProvider(
                MockInitialTeamsProviderSettings(
                    initial_teams=[
                        TeamShell(_id=1, name="A"),
                        TeamShell(_id=2, name="A"),
                    ]
                )
            )

    def test_get__returns_team_objects_when_specifying_projects(self):
        initial_teams = MockInitialTeamsProvider(
            MockInitialTeamsProviderSettings(
                projects=[
                    Project(
                        _id=1,
                        number_of_teams=10,
                    )
                ]
            )
        ).get()
        for team in initial_teams:
            self.assertIsInstance(team, Team)

    def test_get__returns_team_objects_when_specifying_team_shells(self):
        initial_teams = MockInitialTeamsProvider(
            MockInitialTeamsProviderSettings(
                initial_teams=[TeamShell(_id=i) for i in range(10)]
            )
        ).get()
        for team in initial_teams:
            self.assertIsInstance(team, Team)


class TestMockInitialTeamsProviderHelpers(unittest.TestCase):
    def test_projects_to_teams__creates_correct_number_of_teams(self):
        teams_1 = projects_to_teams(
            [
                Project(
                    _id=1,
                    number_of_teams=10,
                )
            ]
        )
        self.assertEqual(len(teams_1), 10)

        teams_2 = projects_to_teams(
            [
                Project(
                    _id=1,
                    number_of_teams=4,
                ),
                Project(
                    _id=1,
                    number_of_teams=3,
                ),
            ]
        )
        self.assertEqual(len(teams_2), 7)

    def test_projects_to_teams__preserves_requirements(self):
        teams = projects_to_teams(
            [
                Project(
                    _id=4,
                    number_of_teams=2,
                    requirements=[
                        ProjectRequirement(
                            attribute=1, operator=RequirementOperator.EXACTLY, value=3
                        )
                    ],
                )
            ]
        )

        for team in teams:
            self.assertTrue(team.requirements)
            self.assertEqual(team.requirements[0].attribute, 1)
            self.assertEqual(team.requirements[0].operator, RequirementOperator.EXACTLY)
            self.assertEqual(team.requirements[0].value, 3)

    def test_projects_to_teams__preserves_project_id_and_name(self):
        teams = projects_to_teams(
            [
                Project(
                    _id=4,
                    name="SpecificName",
                    number_of_teams=2,
                )
            ]
        )

        self.assertEqual(teams[0].name, "SpecificName - 1")
        for team in teams:
            self.assertEqual(team.project_id, 4)

    def test_projects_to_teams__gives_default_team_name(self):
        teams = projects_to_teams(
            [
                Project(
                    _id=4,
                    number_of_teams=2,
                )
            ]
        )

        self.assertEqual(teams[0].name, "Project 4 - 1")
        for team in teams:
            self.assertIsNotNone(team.name)
            self.assertEqual(team.project_id, 4)

    def test_team_shells_to_teams__creates_correct_number_of_teams(self):
        teams = team_shells_to_teams([TeamShell(_id=i) for i in range(10)])
        self.assertEqual(len(teams), 10)

    def test_team_shells_to_teams__preserves_requirements(self):
        teams = team_shells_to_teams(
            [
                TeamShell(
                    _id=4,
                    requirements=[
                        ProjectRequirement(
                            attribute=1, operator=RequirementOperator.EXACTLY, value=3
                        )
                    ],
                )
            ]
        )

        for team in teams:
            self.assertTrue(team.requirements)
            self.assertEqual(team.requirements[0].attribute, 1)
            self.assertEqual(team.requirements[0].operator, RequirementOperator.EXACTLY)
            self.assertEqual(team.requirements[0].value, 3)
