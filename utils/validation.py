from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from benchmarking.data.interfaces import StudentProvider, InitialTeamsProvider


def assert_can_exist_together(
    student_provider: "StudentProvider",
    initial_teams_provider: Optional["InitialTeamsProvider"],
):
    from benchmarking.data.simulated_data.mock_initial_teams_provider import (
        MockInitialTeamsProvider,
    )
    from benchmarking.data.simulated_data.mock_student_provider import (
        MockStudentProvider,
    )

    if (student_provider and not isinstance(student_provider, MockStudentProvider)) or (
        initial_teams_provider
        and not isinstance(initial_teams_provider, MockInitialTeamsProvider)
    ):
        print(
            "[WARNING]: No validation performed on harmony between student and initial teams providers when mock "
            "providers are not being used. Proceed with caution."
        )
        return

    if not student_provider.settings.project_preference_options:
        return

    if (
        student_provider.settings.project_preference_options
        and not initial_teams_provider
    ):
        raise ValueError(
            "Cannot specify project_preference_options without providing projects to match them to."
        )

    if (
        student_provider.settings.project_preference_options
        and initial_teams_provider.settings.projects
    ):
        initial_teams_projects_set = set(
            [p.id for p in initial_teams_provider.settings.projects]
        )
        if not set(student_provider.settings.project_preference_options).issubset(
            initial_teams_projects_set
        ):
            raise ValueError(
                "Mock student provider project preference options can only contain ids present in the projects passed "
                "by the initial teams provider."
            )


def is_non_negative_integer(value: int) -> bool:
    if not isinstance(value, int):
        return False
    if value < 0:
        return False
    return True
