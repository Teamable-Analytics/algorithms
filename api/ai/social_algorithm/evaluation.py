from typing import List, Tuple, Dict

from api.ai.social_algorithm.custom_dataclasses import TeamWithCliques
from api.dataclasses.enums import Relationship
from api.dataclasses.student import Student

UNREGISTERED_STUDENT_ID = -1


class TeamEvaluation:
    def __init__(self, teams: List[TeamWithCliques]):
        self.perfect_team_student_ids: List[int] = [
            student.id for student in TeamEvaluation.get_perfect_team_students(teams)
        ]
        self.teams: List[TeamWithCliques] = teams
        self._students_cache: Dict[
            int, Student
        ] = TeamEvaluation.get_students_from_teams(self.teams)
        self._team_metrics_cache: Dict[
            Tuple[str, bool], Tuple[float, int, int, int]
        ] = {}

    @staticmethod
    def get_students_from_teams(teams: List[TeamWithCliques]) -> Dict[int, Student]:
        students = {}
        for team in teams:
            for student in team.students:
                students[student.id] = student
        return students

    def get_student_by_id(self, student_id: int) -> Student:
        if student_id in self._students_cache:
            return self._students_cache[student_id]
        raise ValueError(f"Student with id {student_id} could not be found.")

    @staticmethod
    def get_perfect_team_students(teams: List[TeamWithCliques]) -> List[Student]:
        perfect_teams = [team for team in teams if team.is_clique]
        students_in_perfect_teams = []
        for perfect_team in perfect_teams:
            students_in_perfect_teams += [student for student in perfect_team.students]
        return students_in_perfect_teams

    @staticmethod
    def is_satisfied(student_id: int, team_member_ids: List[int], friend: bool) -> bool:
        """
        Checks if a preference for student_id is satisfied in team_member_ids
        """
        if not friend:
            return student_id not in team_member_ids
        return student_id in team_member_ids

    @staticmethod
    def opposite_pref(preference_value: Relationship):
        if preference_value == Relationship.ENEMY:
            return Relationship.FRIEND
        if preference_value == Relationship.FRIEND:
            return Relationship.ENEMY

        raise NotImplementedError

    @staticmethod
    def filter_relationships(student: Student, friend: bool) -> List[int]:
        relationship_filter = Relationship.FRIEND if friend else Relationship.ENEMY
        return [
            s_id
            for s_id, relationship in student.relationships.items()
            if relationship == relationship_filter
            and s_id != student.id
            and s_id != UNREGISTERED_STUDENT_ID
        ]

    def is_reach_preference(
        self, pref_giver: Student, pref_target_id: int, friend: bool
    ) -> bool:
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

        if (
            TeamEvaluation.opposite_pref(pref_giver.relationships[pref_target_id])
            == pref_target.relationships[pref_giver.id]
        ):
            return True
        return False

    def team_satisfaction(
        self, team: TeamWithCliques, friend: bool = True
    ) -> Tuple[float, int, int, int]:
        if team.id in self._team_metrics_cache:
            return self._team_metrics_cache[(f"{team.id}", friend)]

        possible_pref_count = 0
        satisfied_pref_count = 0
        reach_pref_count = 0
        team_member_ids = [student.id for student in team.students]

        for student in team.students:
            # filter out people choosing themselves as friends or enemies from affecting the satisfaction score
            relationship_ids = self.filter_relationships(student, friend)
            possible_pref_count += len(relationship_ids)
            satisfied_pref_count += len(
                [
                    s
                    for s in relationship_ids
                    if self.is_satisfied(s, team_member_ids, friend)
                ]
            )

            unsatisfied_pref = [
                s
                for s in relationship_ids
                if not self.is_satisfied(s, team_member_ids, friend)
            ]
            reach_pref_count += len(
                [
                    s
                    for s in unsatisfied_pref
                    if self.is_reach_preference(student, s, friend)
                ]
            )

        if possible_pref_count == 0:
            return 1.0, possible_pref_count, satisfied_pref_count, reach_pref_count

        satisfaction_score = satisfied_pref_count * 1.0 / possible_pref_count
        self._team_metrics_cache[(f"{team.id}", friend)] = (
            satisfaction_score,
            possible_pref_count,
            satisfied_pref_count,
            reach_pref_count,
        )
        return self._team_metrics_cache[(f"{team.id}", friend)]
