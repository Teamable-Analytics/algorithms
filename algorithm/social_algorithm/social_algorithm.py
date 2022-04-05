from typing import List

from algorithm.algorithms import Algorithm
from algorithm.consts import FRIEND
from clique_finder import CliqueFinder
from social_graph import SocialGraph
from algorithm.utility import get_social_utility
from student import Student
from team import Team


class SocialAlgorithm(Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clique_finder = None

    def generate(self, students: [Student], teams: [Team], team_generation_option) -> [Team]:
        # TODO: accounting for locked/pre-set teams is a whole fiesta
        social_graph = SocialGraph(students, FRIEND * 2)
        self.clique_finder = CliqueFinder(students, social_graph)

        # Step 1: Makes teams out of cliques of the correct team size
        clique_student_lists = self.find_clique_teams(students, team_generation_option.max_teams_size)
        for student_list in clique_student_lists:
            empty_team = self.next_empty_team(teams)  # TODO: what if more cliques than team slots
            if empty_team is None:
                break
            self.save_students_to_team(empty_team, student_list)

        # Step 2: fill extra team slots with fragments (largest fragments first)
        k = team_generation_option.min_team_size  # TODO: team of min size + random person? suboptimal
        while self.has_empty_teams(teams) and k > 0:
            clique_student_lists = self.find_clique_teams(students, k)
            if clique_student_lists:  # if cliques of size k are found
                empty_team = self.next_empty_team(teams)
                self.save_students_to_team(empty_team, clique_student_lists[0])  # TODO: not 0
            k -= 1

        # Step 3: fill fragments
        # TODO: change so that we actually loop through biggest cliques remaining and add them to teams?
        """
        CASE:
        Total teams = 5
        Team size = 4
        2 cliques of 4 are found and saved
        4 cliques of 3 are found, only 3 of these are saved due to slots

        Last clique of 3 is now forced to be broken up among the last three team slots
        """
        while self.get_remaining_students(students):
            largest_fragment_team = self.get_largest_fragment_team(teams, team_generation_option)
            if largest_fragment_team is None:
                break

            while largest_fragment_team.size < team_generation_option.min_team_size:
                k = team_generation_option.max_teams_size - largest_fragment_team.size
                all_cliques = self.find_lte_cliques(students, k)
                best_clique, best_clique_score = None, float('-inf')
                for clique in all_cliques:
                    score = self.team_suitability_score(largest_fragment_team, clique)
                    if score > best_clique_score:
                        best_clique = clique
                        best_clique_score = score
                # TODO: rank cliques properly
                # best_clique = all_cliques[0]  # TODO: should be fine mathematically but verify
                self.save_students_to_team(largest_fragment_team, best_clique)

        # Step 4: place last students
        for student in self.get_remaining_students(students):
            single_clique = [student]
            best_team, best_team_score = None, float('-inf')
            for team in self.get_available_teams(teams, team_generation_option):
                # TODO: find best team for single_clique
                curr_score = self.team_suitability_score(team, single_clique)
                if curr_score > best_team_score:
                    best_team = team
                    best_team_score = curr_score
            self.save_students_to_team(best_team, single_clique)

        return teams

    def team_suitability_score(self, team: Team, student_list: List[Student]) -> float:
        if not student_list:
            return None  # cannot be empty TODO: do properly

        overall_utility = 0
        for student in student_list:
            overall_utility += get_social_utility(team, student)
        return overall_utility / len(student_list)  # TODO: replace with scoring function

    def get_largest_fragment_team(self, teams: [Team], team_generation_option) -> Team:
        largest_size = 0
        largest_fragment = None
        for team in teams:
            if team.size >= team_generation_option.min_team_size:
                continue
            if team.size > largest_size:
                largest_fragment = team
                largest_size = team.size
        return largest_fragment  # TODO: what if this returns None

    def is_all_single_cliques(self, cliques: List[List[Student]]) -> bool:
        for clique in cliques:
            if len(clique) > 1:
                return False
        return True

    def find_clique_teams(self, students: [Student], size: int) -> List[List[Student]]:
        clique_ids = self.clique_finder.get_cliques(size)
        if clique_ids is None:
            return []
        clique_student_list = self._clique_ids_to_student_list(students, clique_ids)
        return self.clean_clique_list(clique_student_list)

    def find_lte_cliques(self, students: [Student], size: int) -> List[List[Student]]:
        """
        Multi-memberships are allowed, all cliques of sizes [k...1] are included
        """
        clique_ids = self.clique_finder.find_cliques_lte_size(size)
        if clique_ids is None:
            return []
        clique_student_list = self._clique_ids_to_student_list(students, clique_ids)
        return self.clean_clique_list(clique_student_list)

    def clean_clique_list(self, cliques: List[List[Student]]) -> List[List[Student]]:
        cleaned_cliques = [clique for clique in cliques if self._clique_is_valid(clique)]
        return cleaned_cliques

    def _clique_is_valid(self, clique: List[Student]) -> bool:
        """
        A valid clique in this context means a clique where all members are not already in teams
        """
        for student in clique:
            if student.is_added():
                return False
        return True

    def _clique_ids_to_student_list(self, students: [Student], clique_ids: [int]) -> [[Student]]:
        cliques = []
        for clique in clique_ids:
            clique_students = [student for student in students if student.id in clique]
            cliques.append(clique_students)
        return cliques
