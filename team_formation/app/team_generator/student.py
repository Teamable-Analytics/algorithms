from schema import Schema, SchemaError, Or


class StudentException(Exception):
    pass


class Student:
    """Class used to hold relational information about a student

    Attributes
    ----------
    id: int
        canvas id of student
    skills: dict
        dict of skills
    relationships: dict
        dict of relationships
    preferences: dict
        dict of preferences
    team: Team
        Team object

    Methods
    -------
    is_added
        checks whether or not a student is in a team
    add_team
        sets the team
    get_skill
        gets a specified skill from skills
    """

    def __init__(self, id, skills=None, relationships=None, preferences=None):
        """
        Parameters
        ----------
        id: int
            id of student
        skills: dict
            skills student has:
                { vector_id: [answers], ... }
        relationships: dict
            students relationship with other students:
                { student_id: relationship, ... }
        preferences: dict
            students top preferences for projects:
                { 1: project_id, 2: project_id, 3: project_id, ... }

        Raises
        ------
        StudentException
            given parameters are not in the correct format
        """

        self.id = id
        self.skills = skills or {}
        self.relationships = relationships or {}
        self.preferences = preferences or {}
        self.team = None
        self.validate()

    def validate(self):
        try:
            Schema(int).validate(self.id)
            Schema(Or({int: [int, float]}, {})).validate(self.skills)
            Schema(Or({int: Or(int, float)}, {})).validate(self.relationships)
            Schema(Or({int: int}, {})).validate(self.preferences)
            for counter, _ in enumerate(self.preferences.keys(), start=1):
                if not self.preferences.get(counter, None):
                    raise SchemaError('Preferences keys are not in increasing order starting from 1')
        except SchemaError as error:
            raise StudentException(f'Error while initializing student: \n{error}')

    def is_added(self):
        """Check whether or not a student is in a team"""
        return self.team is not None

    def add_team(self, team):
        """Set team

        Parameters
        ----------
        team: Team
            team object

        Returns
        -------
        bool
            students team was set
        """
        if self.team:
            return False
        self.team = team
        return True

    def remove_team(self):
        """Remove team

        Parameters
        ----------
        team: Team
            team object

        Returns
        -------
        bool
            students team was removed
        """
        self.team = None
        return True

    def get_skill(self, vector_id):
        """Get a skill that matches specified vector id

        Parameters
        ----------
        vector_id: int
            id of vector

        Returns
        -------
        list
            list of answers
        """
        return self.skills.get(vector_id, [])
