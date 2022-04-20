from schema import Schema, SchemaError, Or
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.algorithm.consts import REQUIREMENT_TYPES


class TeamException(Exception):
    pass


class Team:
    """Class used to represent a team

    Attributes
    ----------
    id: int
        id of team
    name: str
        name of the team
    students: list
        list of Students
    requirements: list
        list of team requirements

    Methods
    -------
    students_satisfied_requirements
        returns the number of currently unmet requirements that this student satisfies
    requirement_met_by_student
        checks if a student meets any given requirement
    add_student
        add student to team if they do not exist in another

    Properties
    ----------
    size
        get the size of the team
    is_locked
        whether or not the team can be modified
    """

    students = []

    def __init__(self, id: str, project_id: int, name: str, students: list = None, requirements: list = None, locked: bool = False):
        """
        Parameters
        ----------
        id: str
            the id (surrogate key) of the team stored in order
        project_id: int
            the id of this team (used so student preferences can be matched to teams)
        name: str
            the name of the team
        students: list
            a list of Student objects
        requirements: list
            [{
                'id': int (id of the requirement),
                'operator': str ('includes', 'exactly', 'less than', 'greater than'),
                'value': int,
            }, ...]
        locked: bool
            whether or not the team can be modified

        Raises
        ------
        TeamException
            Error while initializing team
        """

        self.id = id
        self.project_id = project_id
        self.name = name
        self.students = students or []
        self.requirements = requirements or []
        self._locked = locked
        self.is_clique = False
        self.validate()

    def validate(self):
        try:
            Schema(str).validate(self.id)
            Schema(int).validate(self.project_id)
            Schema(str).validate(self.name)
            self.students = Schema([Student]).validate(self.students)
            for student in self.students:
                student.add_team(self)
            self.requirements = Schema([{
                'id': int,
                'operator': Or(REQUIREMENT_TYPES.EXACTLY, REQUIREMENT_TYPES.LESS_THAN, REQUIREMENT_TYPES.MORE_THAN),
                'value': int
            }]).validate(self.requirements)
            Schema(bool).validate(self._locked)
        except SchemaError as error:
            raise TeamException(f'Error while initializing team: \n{error}')

    def student_satisfied_requirements(self, student):
        """Returns the number of currently unmet requirements that this student satisfies

        Parameters
        ----------
        student: Student
            Student object

        Returns
        -------
        int
            number of currently unmet requirements
        """

        unmet_requirements = []
        for requirement in self.requirements:
            satisfied = False
            for s in self.students:
                satisfied = self.requirement_met_by_student(requirement, s)
                if satisfied:
                    break
            if not satisfied:
                unmet_requirements.append(requirement)

        unmet_requirements_satisfied = 0
        for requirement in unmet_requirements:
            unmet_requirements_satisfied += self.requirement_met_by_student(requirement, student)

        return unmet_requirements_satisfied

    def requirement_met_by_student(self, requirement, student):
        """Checks if a student meets any given requirement

        Gets the skill from student, ensuring that it is a list of answers. Looping
        through the answers, it checks whether or not each answer meets the requirements,
        if not it fails the test. If there are no problems then it passes.

        Parameters
        ----------
        requirement: dict
            dict of { id: int, operator: str ('includes', 'exactly', 'less than', 'greater than'), value: int }
        student: Student
            student of Student class

        Returns
        -------
        bool
            whether or not student has met requirement
        """

        is_met = False
        for value in student.get_skill(requirement['id']):
            if requirement['operator'] == REQUIREMENT_TYPES.LESS_THAN:
                is_met |= (value < requirement['value'])
            elif requirement['operator'] == REQUIREMENT_TYPES.MORE_THAN:
                is_met |= (value > requirement['value'])
            else:  # default case is 'exactly'
                is_met |= (value == requirement['value'])
        return is_met

    def student_get_requirements(self, student):
        """Get the amount of requirements a student meets

        Parameters
        ----------
        student: Student
            Student object

        Returns
        -------
        int
            number of requirements met
        """

        total_requirements = 0
        for requirement in self.requirements:
            total_requirements += self.requirement_met_by_student(requirement, student)
        return total_requirements

    def total_requirements(self):
        """Get the total requirements"""
        return len(self.requirements)

    def add_student(self, student):
        """Add student to team if they do not exist in another

        Parameters
        ----------
        student: Student
            Student object

        Returns
        -------
        bool
            whether or not the student was added successfully
        """

        if self.is_locked or student.is_added():
            return False
        self.students.append(student)
        return True

    def remove_student(self, student):
        """Remove student from team

        Parameters
        ----------
        student: Student
            Student object

        Return
        ------
        bool
            whether or not the student was remove successfully
        """
        if self.is_locked:
            return False
        self.students.remove(student)
        return True

    def get_students(self):
        """Returns a duplicate array of the same student objects

        Return
        ------
        list
            list of Student objects
        """
        return [student for student in self.students]

    @property
    def size(self):
        """Get the size of the team"""
        return len(self.students)

    @property
    def is_locked(self):
        """Whether or not team is locked"""
        return self._locked

    def set_clique(self):
        self.is_clique = True

    def lock(self):
        self._locked = True
