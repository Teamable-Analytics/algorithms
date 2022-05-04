import random
from typing import List, Tuple

from schema import Schema, SchemaError

from team_formation.app.team_generator.algorithm.consts import FRIEND, DEFAULT, ENEMY
from team_formation.app.team_generator.algorithm.utility import get_requirement_utility, get_social_utility, \
    get_diversity_utility, get_preference_utility
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team


class AlgorithmException(Exception):
    pass


class AlgorithmOptions:
    """
    Validates and stores the relevant information for algorithms to use.

    Parameters:
    requirement_weight: weight for how much the matching of student skills to project requirements matters
    social_weight: how likely it is for students to be on teams with their whitelisted students and
                    not on teams with their blacklisted students
    diversity_weight: how much the "concentrate_options" and "diversify_options" play a role preference_weight:
                    how much a student's project preference matters
    max_project_preferences: if allowed to be specified, this is the maximum number of projects any student was
                    able to specify as a ranked preference

    concentrate_options & diversify_options: [ {id: int}...]
    concentrate_options: Ensure that people with these skill are all on the same team as much as possible
    diversify_options: Ensure that people with these skill are all on different teams as much as possible

    priorities: [{
        order: int,
        type: str,
        id: int,
        max_of: int (a maximum of this many students with this skill on a team ideally),    -- -1 if unspecified
        min_of: int (a minimum of this many students with this skill on a team ideally),    -- -1 if unspecified
        value: int (the value that max_of and min_of are applied to),                       -- -1 if unspecified
    }...]
    priorities: both 'max_of' and 'min_of' cannot be specified at the same time
    """

    BEHAVIOUR_OPTIONS = {
        'ENFORCE': 'enforce',
        'INVERT': 'invert',
        'IGNORE': 'ignore',
    }

    def __init__(self, requirement_weight: int = None, social_weight: int = None, diversity_weight: int = None,
                 preference_weight: int = None, max_project_preferences: int = None, blacklist_behaviour: str = None,
                 whitelist_behaviour: str = None, diversify_options: List[dict] = None,
                 concentrate_options: List[dict] = None,
                 priorities: List[dict] = None):
        self.diversity_weight = diversity_weight
        self.preference_weight = preference_weight
        self.requirement_weight = requirement_weight
        self.social_weight = social_weight

        self.max_project_preferences = max_project_preferences

        self.blacklist_behaviour = blacklist_behaviour or self.BEHAVIOUR_OPTIONS['IGNORE']
        self.whitelist_behaviour = whitelist_behaviour or self.BEHAVIOUR_OPTIONS['IGNORE']

        self.diversify_options = diversify_options or []
        self.concentrate_options = concentrate_options or []

        self.priorities = priorities or []
        self.priorities = sorted(self.priorities, key=lambda priority: priority['order'])
        self.validate()

    def validate(self):
        validate_int = [self.diversity_weight, self.preference_weight, self.requirement_weight, self.social_weight,
                        self.max_project_preferences]
        for item in validate_int:
            if item and not isinstance(item, int):
                raise AlgorithmException('One or more of "diversity weight", "preference weight", "requirement '
                                         'weight", "social weight", "max preferences" is not an integer.')

        validate_str = [self.blacklist_behaviour, self.whitelist_behaviour]
        for item in validate_str:
            if not isinstance(item, str):
                raise AlgorithmException('One or more of "blacklist behaviour", "whitelist behaviour" is not a string.')
            if item not in self.BEHAVIOUR_OPTIONS.values():
                raise AlgorithmException('Invalid behaviour option.')

        validate_options_list = [self.concentrate_options, self.diversify_options]
        try:
            Schema([[{'id': int}]]).validate(validate_options_list)
        except SchemaError as se:
            raise AlgorithmException('Invalid format for concentrate/diversify options', se)

        # Validate Priorities
        priorities_schema = Schema([{'order': int, 'constraint': str, 'skill_id': int, 'limit_option': str, 'limit': int, 'value': int}])

        try:
            priorities_schema.validate(self.priorities)
        except SchemaError as se:
            raise AlgorithmException('Invalid format for "priorities"', se)

    def get_adjusted_relationships(self) -> Tuple[dict, bool]:
        """
        Computes the adjusted relationships based on the whitelist and blacklist behaviours.

        Returns
        -------
        (dict, bool)
            A dictionary containing mappings of relationships to their adjusted form and a boolean that identifies if
            any relationships were indeed adjusted
        """
        adjusted_relationships = {
            FRIEND: FRIEND,
            DEFAULT: DEFAULT,
            ENEMY: ENEMY,
        }

        # the ENFORCE option is assumed unless one of the conditions below changes the default behaviour
        if self.whitelist_behaviour == AlgorithmOptions.BEHAVIOUR_OPTIONS['INVERT']:
            adjusted_relationships[FRIEND] = ENEMY
        elif self.whitelist_behaviour == AlgorithmOptions.BEHAVIOUR_OPTIONS['IGNORE']:
            adjusted_relationships[FRIEND] = DEFAULT

        if self.blacklist_behaviour == AlgorithmOptions.BEHAVIOUR_OPTIONS['INVERT']:
            adjusted_relationships[ENEMY] = FRIEND
        elif self.blacklist_behaviour == AlgorithmOptions.BEHAVIOUR_OPTIONS['IGNORE']:
            adjusted_relationships[ENEMY] = DEFAULT

        is_modified = False
        for relationship, adj_relationship in adjusted_relationships.items():
            if relationship != adj_relationship:
                is_modified = True
                break

        return adjusted_relationships, is_modified


class Algorithm:
    """Class used to define the basic functions and validate data of an algorithm

    Attributes
    ----------
    options: AlgorithmOptions
        algorithm options
    """

    def __init__(self, options: AlgorithmOptions, logger=None):
        """
        Parameters
        ----------
        options: AlgorithmOptions
            algorithm options
        logger: Logger
        """
        try:
            self.options = Schema(AlgorithmOptions).validate(options)
        except SchemaError as error:
            raise AlgorithmException(f'Error while initializing class: \n{error}')
        self.teams = []
        self.logger = logger
        self.stage = 1

    def generate(self, students, teams, team_generation_option) -> List[Team]:
        raise NotImplementedError()

    def get_remaining_students(self, all_students: List[Student]) -> List[Student]:
        return [student for student in all_students if not student.is_added()]

    def get_available_teams(self, all_teams: List[Team], team_generation_option, student: Student = None) -> List[Team]:
        """
        Returns a list of teams available to be joined by a student. If a specific Student is provided, only returns
        teams that that specific student is able to join.

        Parameters
        ----------
        all_teams: List[Team]
            algorithm options
        team_generation_option: TeamGenerationOption
            team generation option
        student: Student
            if given, only returns the available teams that the provided student can join

        Returns
        -------
        List[Team]
            The available teams
        """
        available_teams = []
        for team in all_teams:
            if team.size < team_generation_option.max_teams_size and not team.is_locked:
                if not student:
                    available_teams.append(team)
                elif student and self.student_permitted_in_team(student, team):
                    available_teams.append(team)

        return available_teams

    def student_permitted_in_team(self, student: Student, team: Team) -> bool:
        """Can be overridden in Algorithms to support custom rules for whether a student can be added to a team"""
        return True

    def save_students_to_team(self, team: Team, student_list: List[Student]):
        for student in student_list:
            team.add_student(student)
            student.add_team(team)

    def next_empty_team(self) -> Team:
        for team in self.teams:
            if team.size == 0:
                return team

    def has_empty_teams(self) -> bool:
        next_empty_team = self.next_empty_team()
        return bool(next_empty_team)

    def increment_stage(self):
        self.stage += 1


class WeightAlgorithm(Algorithm):
    """Class used to select teams using a weight algorithm

    Methods
    -------
    generate
        generate a set of teams using this algorithm
    choose
        choose the smallest team and the student that has the highest utility for that team
    """

    def generate(self, students, teams, team_generation_option) -> List[Team]:
        return _generate_with_choose(self, students, teams, team_generation_option)

    def choose(self, teams, students):
        """Choose the smallest team and the student that has the highest utility for that team

        Returns
        -------
        (Team, Student)
            the smallest team and the highest utility student for that team
        """

        smallest_team = None
        for team in teams:
            if smallest_team is None or team.size < smallest_team.size:
                smallest_team = team

        if not smallest_team:
            return None, None

        greatest_utility = 0
        greatest_utility_student = None
        for student in students:
            utility = self._get_utility(smallest_team, student)
            if greatest_utility_student is None or utility > greatest_utility:
                greatest_utility = utility
                greatest_utility_student = student

        return smallest_team, greatest_utility_student

    def _get_utility(self, team, student):
        """Get the combined utility

        Get the utility for each of the four weights, requirement/social/diversity/preference.
        Then combine each of the normalized weights. Each utility is modified based on the options.

        Parameters
        ----------
        team: Team
            specified team
        student: Student
            specified student

        Returns
        -------
        float
            combined utility
        """

        if student in team.get_students():
            return 0

        requirement_utility = get_requirement_utility(team, student) * self.options.requirement_weight
        social_utility = get_social_utility(team, [student]) * self.options.social_weight
        diversity_utility = get_diversity_utility(
            team, student,
            self.options.diversify_options,
            self.options.concentrate_options) * self.options.diversity_weight
        preference_utility = get_preference_utility(
            team, student,
            self.options.max_project_preferences) * self.options.preference_weight

        return requirement_utility + social_utility + diversity_utility + preference_utility


class RandomAlgorithm(Algorithm):
    """Class used to select teams using a random algorithm

    Methods
    -------
    generate
        generate a set of teams using this algorithm
    choose
        choose a random team and a random student
    """

    def generate(self, students, teams, team_generation_option) -> List[Team]:
        return _generate_with_choose(self, students, teams, team_generation_option)

    def choose(self, teams, students):
        """Choose the smallest team and a random student

        Returns
        -------
        (Team, Student)
            a random team and a random student
        """

        smallest_team = None
        for team in teams:
            if smallest_team is None or team.size < smallest_team.size:
                smallest_team = team
        student_size = len(students)

        if not smallest_team or not student_size:
            return None, None

        random_student = students[random.randint(0, student_size - 1)]

        return smallest_team, random_student


def _generate_with_choose(algorithm, students, teams, team_generation_option) -> List[Team]:
    while True:
        available_teams = algorithm.get_available_teams(teams, team_generation_option)
        remaining_students = algorithm.get_remaining_students(students)
        team, student = algorithm.choose(available_teams, remaining_students)
        if not team or not student:
            break
        algorithm.save_students_to_team(team, [student])
    return teams
