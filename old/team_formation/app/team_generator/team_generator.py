from schema import Schema, And, SchemaError
from old.team_formation.app.team_generator.algorithm.algorithms import Algorithm
from old.team_formation.app.team_generator.algorithm.consts import REQUIREMENT_TYPES
from old.team_formation.app.team_generator.student import Student
from old.team_formation.app.team_generator.team import Team
from old.team_formation.app.team_generator.validation import validate_unique_fields


class TeamGenerationException(Exception):
    pass


class TeamGenerationOption:
    """
    Stores options relating to team generation

    Attributes
    ----------
    max_team_size: int
        every team created must have <= this number of students in it
    min_team_size: int
        every team created must have >= this number of students in it -- enforced after total_teams
    total_teams: int
        the total number of teams to be created
    team_options: list
        list of team options containing requirements and team data
    """

    def __init__(
        self,
        max_team_size: int,
        min_team_size: int,
        total_teams: int,
        team_options: list,
    ):
        """
        Parameters
        ----------
        max_team_size: int
            every team created must have <= this number of students in it
        min_team_size: int
            every team created must have >= this number of students in it -- enforced after total_teams
        total_teams: int
            the total number of teams to be created
        team_options: list
            [{
                id: int                 (id of the team this option applies to),
                project_id: int         (id of the project related to this team, if there is one),
                name: str               (name of the team this option applies to),
                requirements: [{
                    id: int             (id of the skill that this requirement refers to),
                    value: int          (the value threshold needed to 'pass' this requirement),
        SOON        operator: string,   (the operator to define 'passing'. one of 'less than', 'more than', 'exactly')
                }
                ...]
            }
            ...]

        Raises
        ------
        TeamGenerationException
            invalid parameters
        """

        self.max_teams_size = max_team_size
        self.min_team_size = min_team_size
        self.total_teams = total_teams
        self.team_options = team_options
        self.validate()

    def validate(self):
        """Validate data"""

        conf_schema = Schema(
            [
                {
                    "id": str,
                    "project_id": int,
                    "name": str,
                    "requirements": [
                        {
                            "id": int,
                            "value": int,
                            "operator": And(
                                str,
                                lambda n: n
                                in [
                                    REQUIREMENT_TYPES.MORE_THAN,
                                    REQUIREMENT_TYPES.LESS_THAN,
                                    REQUIREMENT_TYPES.EXACTLY,
                                ],
                            ),
                        }
                    ],
                }
            ]
        )
        try:
            conf_schema.validate(self.team_options)
            validate_unique_fields(
                self.team_options,
                TeamGenerationException,
                field="id",
                set_name="team options",
            )
        except SchemaError as se:
            raise TeamGenerationException('Invalid format for "team options"', se)
        try:
            if len(self.team_options) > self.total_teams:
                raise TeamGenerationException(
                    "There are more requirements than there can be teams!"
                )
        except TypeError as te:
            raise TeamGenerationException(
                "Invalid parameters causing logic issues:", te
            )

        validate_int = [self.max_teams_size, self.min_team_size, self.total_teams]
        for item in validate_int:
            if item and not isinstance(item, int):
                raise TeamGenerationException(
                    'One or more of "max team size", "min team size", and "total teams" is '
                    "not an integer"
                )
        if self.max_teams_size < self.min_team_size:
            raise TeamGenerationException(
                "The minimum team size is greater than the maximum team size!"
            )


class TeamGenerator:
    """Class used to generate teams

    Attributes
    ----------
    students: [Students]
        list of students
    algorithm: Algorithm
        algorithm class
    options: TeamGenerationOption
        team generation options class
    teams: list
        list of Team objects

    Methods
    -------
    generate
        generate teams
    create_teams
        create teams
    get_remaining_student
        get the remaining students not in a team
    get_available_teams
        get teams that are available to fill
    """

    def __init__(
        self,
        students,
        algorithm: Algorithm,
        initial_teams: list,
        options: TeamGenerationOption,
    ):
        """
        Parameters
        ----------
        students: [Students]
            list of students
        algorithm: Algorithm
            algorithm class
        initial_teams: list
            list of initial Team objects with Students
        options: TeamGenerationOption
            team generation options class

        Raises
        ------
        TeamGenerationException
            invalid parameters
        """

        try:
            self.students = Schema([Student]).validate(students)
            self.algorithm: Algorithm = Schema(Algorithm).validate(algorithm)
            self.options = Schema(TeamGenerationOption).validate(options)
            self.teams = self.create_teams(Schema([Team]).validate(initial_teams))
        except SchemaError as error:
            raise TeamGenerationException(f"Invalid parameters: \n{error}")

    def generate(self):
        return self.algorithm.generate(self.students, self.teams, self.options)

    def create_teams(self, initial_teams):
        """Create teams

        Creates empty teams based on the specified options. If the team
        size option is not met, teams are continually generated until met.

        Parameters
        ----------
        initial_teams: list
            list of initial Team objects with Students

        Returns
        -------
        list
            list of Team objects
        """

        teams = initial_teams
        for team_option in self.options.initial_teams:
            for team in initial_teams:
                if team.id == team_option["id"]:
                    break
            else:
                teams.append(
                    Team(
                        team_option["id"],
                        team_option["project_id"],
                        team_option["name"],
                        students=None,
                        requirements=team_option["requirements"],
                    )
                )

        # Create the remaining teams with unique names
        counter = 1
        while len(teams) < self.options.total_teams:
            name = f"Team {counter}"
            if name not in map(lambda t: t.name, teams):
                teams.append(Team("-1", -1, name))
            counter += 1

        return teams


def generate_teams(
    course_id,
    section_ids,
    survey_id,
    excluded_students_ids: [],
    excluded_team_ids: [],
    data_loader,
):
    """Generate teams

    Parameters
    ----------
    course_id: int
        id of the course
    section_ids: [int]
        list of ids of the sections
    survey_id: int
        id of the survey
    excluded_students_ids: list
        list of students to exclude from team generation
    excluded_team_ids: list
        list of team ids to exclude from team generation
    data_loader: DataLoader
        DataLoader object

    Returns
    -------
    list
        list of Team objects

    Raises
    ------
    DataLoaderException
        if no response could be found for a student in a survey /
        algorithm type could not be found /
        could not find team size options
    TeamGenerationException
        invalid team generation parameters
    """
    algorithm = data_loader.get_algorithm()

    students = data_loader.get_students_with_updated_relationships(
        course_id,
        section_ids,
        survey_id,
        algorithm.options,
        excluded_students_ids,
    )

    team_generation_options = data_loader.get_team_generation_options()

    excluded_teams = data_loader.get_teams_from_excluded_teams(
        excluded_team_ids, students, team_generation_options
    )

    team_generator = TeamGenerator(
        students, algorithm, excluded_teams, team_generation_options
    )
    teams = team_generator.generate()

    return teams
