import itertools
from typing import List

import numpy as np

from api.dataclasses.enums import (
    AttributeValueEnum,
    ScenarioAttribute,
    Gender,
    Race,
    RequirementOperator,
)
from api.dataclasses.project import Project, ProjectRequirement
from api.dataclasses.student import Student
from api.dataclasses.team import TeamShell
from benchmarking.data.interfaces import StudentProvider, InitialTeamsProvider
from benchmarking.data.simulated_data.mock_initial_teams_provider import (
    MockInitialTeamsProvider,
    MockInitialTeamsProviderSettings,
)
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
    MockStudentProviderSettings,
)


TECHNICAL_SKILLS = 410
GITHUB_EXPERIENCE = 411
WORK_EXPERIENCE = 412


class DevelopmentSkills(AttributeValueEnum):
    Typescript = 1
    Next = 2
    Python = 3
    Django = 4
    Backend = 5
    Frontend = 6
    Design = 7
    ReactNative = 8
    Mobile = 9
    AWS = 10


class GithubExperience(AttributeValueEnum):
    Beginner = 1  # What is git
    Intermediate = 2  # meaning you know how to push stuff to git
    Advanced = (
        3  # Meaning you know more than git add ., git commit -m, git push, git status
    )


class WorkExperience(AttributeValueEnum):
    No_Experience = 1
    One_Semester = 2
    Two_Semesters = 3
    Three_Semesters = 4
    More_Than_Three_Semesters = 5


class RealisticMockStudentProvider(StudentProvider):
    def __init__(
        self,
        class_size: int,
        ratio_of_female_students: float = 0.2,
        ratio_of_african_students: float = 0.15,
    ):
        self.class_size = class_size
        self.ratio_of_female_students = ratio_of_female_students
        self.ratio_of_african_students = ratio_of_african_students

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0  # Yes, students have no choice (because it's UBC)

    @property
    def num_students(self) -> int:
        return self.class_size

    def get(self, seed: int = None) -> List[Student]:
        students = MockStudentProvider(
            settings=MockStudentProviderSettings(
                number_of_students=self.class_size,
                attribute_ranges={
                    ScenarioAttribute.GENDER.value: [
                        (Gender.MALE, 1 - self.ratio_of_female_students),
                        (Gender.FEMALE, self.ratio_of_female_students),
                    ],
                    ScenarioAttribute.RACE.value: [
                        (Race.African, self.ratio_of_african_students),
                        (Race.European, 1 - self.ratio_of_african_students),
                    ],
                    ScenarioAttribute.YEAR_LEVEL.value: [
                        (0, 0.3),
                        (1, 0.25),
                        (2, 0.2),
                        (3, 0.2),
                        (4, 0.05),
                    ],
                    GITHUB_EXPERIENCE: [
                        (GithubExperience.Beginner, 0.2),
                        (GithubExperience.Intermediate, 0.7),
                        (GithubExperience.Advanced, 0.1),
                    ],
                    WORK_EXPERIENCE: [
                        (WorkExperience.No_Experience, 0.4),
                        (WorkExperience.One_Semester, 0.05),
                        (WorkExperience.Two_Semesters, 0.2),
                        (WorkExperience.Three_Semesters, 0.3),
                        (WorkExperience.More_Than_Three_Semesters, 0.05),
                    ],
                },
            )
        ).get()

        # Edit to add skills
        skills = [
            (DevelopmentSkills.Typescript.value, 0.4),
            (DevelopmentSkills.Next.value, 0.3),
            (DevelopmentSkills.Python.value, 0.8),
            (DevelopmentSkills.Django.value, 0.1),
            (DevelopmentSkills.Backend.value, 0.3),
            (DevelopmentSkills.Frontend.value, 0.6),
            (DevelopmentSkills.Design.value, 0.4),
            (DevelopmentSkills.ReactNative.value, 0.2),
            (DevelopmentSkills.Mobile.value, 0.8),
            (DevelopmentSkills.AWS.value, 0.2),
        ]

        rng = np.random.default_rng(seed=seed)
        for student in students:
            student.attributes[TECHNICAL_SKILLS] = []
            for skill, chance in skills:
                if rng.random() < chance:
                    student.attributes[TECHNICAL_SKILLS].append(skill)

        order = rng.permutation(len(students))
        return [students[_] for _ in order]


class RealisticMockInitialTeamsProvider(InitialTeamsProvider):
    def __init__(self, num_teams: int):
        self.num_teams = num_teams

    def get(self) -> List[TeamShell]:
        projects = []
        project_cycler = itertools.cycle(get_realistic_projects())
        for i in range(self.num_teams):
            next_project = next(project_cycler)
            projects.append(
                Project(
                    _id=i,
                    name=next_project.name + " " + str(i),
                    requirements=next_project.requirements,
                )
            )
        return MockInitialTeamsProvider(
            settings=MockInitialTeamsProviderSettings(
                projects=projects,
            )
        ).get()


def get_realistic_projects() -> List[Project]:
    """
    A list of five projects with realistic requirements.
    Each project has 3-5 requirements.
    """
    return [
        Project(
            _id=1,
            name="Face blur video sending and receiving using Amazon Web Services (AWS)",
            requirements=[
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.AWS.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Frontend.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Backend.value,
                ),
                ProjectRequirement(
                    attribute=WORK_EXPERIENCE,
                    operator=RequirementOperator.MORE_THAN,
                    value=WorkExperience.Two_Semesters.value,
                ),
                ProjectRequirement(
                    attribute=GITHUB_EXPERIENCE,
                    operator=RequirementOperator.MORE_THAN,
                    value=GithubExperience.Beginner.value,
                ),
            ],
        ),
        Project(
            _id=2,
            name="Left over food delivery mobile app",
            requirements=[
                ProjectRequirement(
                    attribute=WORK_EXPERIENCE,
                    operator=RequirementOperator.LESS_THAN,
                    value=WorkExperience.Two_Semesters.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Mobile.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.ReactNative.value,
                ),
            ],
        ),
        Project(
            _id=3,
            name="Collaborative website to play games with each other using PyGame",
            requirements=[
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Python.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Frontend.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Design.value,
                ),
                ProjectRequirement(
                    attribute=GITHUB_EXPERIENCE,
                    operator=RequirementOperator.EXACTLY,
                    value=GithubExperience.Advanced.value,
                ),
            ],
        ),
        Project(
            _id=4,
            name="Create an Internal Website for Scheduling for a Company",
            requirements=[
                ProjectRequirement(
                    attribute=WORK_EXPERIENCE,
                    operator=RequirementOperator.LESS_THAN,
                    value=WorkExperience.Two_Semesters.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Backend.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Next.value,
                ),
            ],
        ),
        Project(
            _id=5,
            name="Dating app for pets",
            requirements=[
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Mobile.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Backend.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Frontend.value,
                ),
                ProjectRequirement(
                    attribute=TECHNICAL_SKILLS,
                    operator=RequirementOperator.EXACTLY,
                    value=DevelopmentSkills.Django.value,
                ),
            ],
        ),
    ]
