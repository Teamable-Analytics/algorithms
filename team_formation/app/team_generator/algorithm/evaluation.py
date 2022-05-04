from typing import List, Tuple, Dict

from team_formation.app.team_generator.algorithm.consts import FRIEND, ENEMY, UNREGISTERED_STUDENT_ID
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team


class TeamEvaluation:
    def __init__(self, teams: List[Team]):
        self.perfect_team_student_ids: List[int] = [student.id for student in self.get_perfect_team_students(teams)]
        self.teams: List[Team] = teams
        self._students_cache: Dict[int, Student] = self.get_students_from_teams(self.teams)
        self._team_metrics_cache: Dict[Tuple[str, bool], Tuple[float, int, int, int]] = {}

    def get_students_from_teams(self, teams: List[Team]) -> Dict[int, Student]:
        students = {}
        for team in teams:
            for student in team.students:
                students[student.id] = student
        return students

    def get_student_by_id(self, student_id: int) -> Student:
        if student_id in self._students_cache:
            return self._students_cache[student_id]
        raise ValueError(f'Student with id {student_id} could not be found.')

    def get_perfect_team_students(self, teams: List[Team]) -> List[Student]:
        perfect_teams = [team for team in teams if team.is_clique]
        students_in_perfect_teams = []
        for perfect_team in perfect_teams:
            students_in_perfect_teams += [student for student in perfect_team.students]
        return students_in_perfect_teams

    def is_satisfied(self, student_id: int, team_member_ids: List[int], friend: bool) -> bool:
        """
        Checks if a preference for student_id is satisfied in team_member_ids
        """
        if not friend:
            return student_id not in team_member_ids
        return student_id in team_member_ids

    def opposite_pref(self, preference_value: float):
        if preference_value == ENEMY:
            return FRIEND
        if preference_value == FRIEND:
            return ENEMY
        return False

    def filter_relationships(self, student: Student, friend: bool) -> List[int]:
        relationship_filter = FRIEND if friend else ENEMY
        return [s_id for s_id, relationship in student.relationships.items()
                if relationship == relationship_filter
                and s_id != student.id
                and s_id != UNREGISTERED_STUDENT_ID]

    def is_reach_preference(self, pref_giver: Student, pref_target_id: int, friend: bool) -> bool:
        """
        Reaches are:
            - Person A friend Person B but Person B indicated A as an enemy (or vice versa)
            - Person A friend Person B but Person B is in a perfect group (all perfectly interconnected)
        """
        if friend and pref_target_id in self.perfect_team_student_ids:
            return True
        if pref_target_id not in pref_giver.relationships:
            return False

        pref_target = self.get_student_by_id(pref_target_id)
        if pref_giver.id not in pref_target.relationships:
            return False

        if self.opposite_pref(pref_giver.relationships[pref_target_id]) == pref_target.relationships[pref_giver.id]:
            return True
        return False

    def team_satisfaction(self, team: Team, friend: bool = True) -> Tuple[float, int, int, int]:
        if team.id in self._team_metrics_cache:
            return self._team_metrics_cache[(team.id, friend)]

        possible_pref_count = 0
        satisfied_pref_count = 0
        reach_pref_count = 0
        team_member_ids = [student.id for student in team.students]

        for student in team.students:
            # filter out people choosing themselves as friends or enemies from affecting the satisfaction score
            relationship_ids = self.filter_relationships(student, friend)
            possible_pref_count += len(relationship_ids)
            satisfied_pref_count += len([s for s in relationship_ids if self.is_satisfied(s, team_member_ids, friend)])

            unsatisfied_pref = [s for s in relationship_ids if not self.is_satisfied(s, team_member_ids, friend)]
            reach_pref_count += len([s for s in unsatisfied_pref if self.is_reach_preference(student, s, friend)])

        if possible_pref_count == 0:
            return 1.0, possible_pref_count, satisfied_pref_count, reach_pref_count

        satisfaction_score = satisfied_pref_count * 1.0 / possible_pref_count
        self._team_metrics_cache[(team.id, friend)] = \
            satisfaction_score, possible_pref_count, satisfied_pref_count, reach_pref_count
        return self._team_metrics_cache[(team.id, friend)]

    def team_satisfaction_score(self, team: Team, friend=True) -> float:
        score, _, _, _ = self.team_satisfaction(team, friend)
        return score

    def team_set_satisfaction_score(self, friend: bool = True) -> float:
        if not self.teams:
            return 0

        possible_pref = 0
        satisfied_pref = 0
        for team in self.teams:
            _, possible, satisfied, _ = self.team_satisfaction(team, friend)
            possible_pref += possible
            satisfied_pref += satisfied

        if possible_pref == 0:
            return 1.0

        satisfaction_score = satisfied_pref / possible_pref
        return satisfaction_score

    def team_set_satisfaction_metrics(self, friend: bool = True) -> Tuple[int, int, int, int]:
        number_possible, number_satisfied, num_reach = 0, 0, 0
        for team in self.teams:
            _, team_possible, team_satisfied, reach = self.team_satisfaction(team, friend)
            number_possible += team_possible
            number_satisfied += team_satisfied
            num_reach += reach
        number_missed = number_possible - num_reach - number_satisfied
        return number_satisfied, num_reach, number_missed, number_possible

