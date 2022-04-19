from typing import List

from team_formation.app.team_generator.algorithm.algorithms import Algorithm, _generate_with_choose
from team_formation.app.team_generator.algorithm.consts import FRIEND
from team_formation.app.team_generator.algorithm.social_algorithm.clique_finder import CliqueFinder
from team_formation.app.team_generator.algorithm.social_algorithm.social_graph import SocialGraph
from team_formation.app.team_generator.algorithm.utility import get_social_utility, get_requirement_utility, \
    get_diversity_utility, get_preference_utility
from team_formation.app.team_generator.student import Student
from team_formation.app.team_generator.team import Team


class SocialAlgorithm(Algorithm):
    def __init__(self, algorithm_options, logger, *args, **kwargs):
        super().__init__(algorithm_options, logger)
        self.clique_finder = None

    def generate(self, students: [Student], teams: [Team], team_generation_option) -> [Team]:
        # TODO: should work with preset teams, but check this behaviour
        self.teams = teams
        # TODO: this level should be more inclusive if we are regenerating, it's unlikely people give even their friends
        #  a perfect peer evaluation
        social_graph = SocialGraph(students, FRIEND * 2)
        self.clique_finder = CliqueFinder(students, social_graph)
        # find all cliques of all sizes, so that they are cached for later
        self.clique_finder.find_cliques_lte_size(team_generation_option.max_teams_size)

        # Step 1: Makes teams out of cliques of the correct team size
        clique_student_lists = self.find_clique_teams(students, team_generation_option.max_teams_size, clean=True)
        for student_list in clique_student_lists:
            empty_team = self.next_empty_team()
            if empty_team is None:
                break
            self.save_students_to_team(empty_team, student_list)
            empty_team.lock()

        self.increment_stage()

        # Step 2: fill extra team slots with fragments (largest fragments first)
        k = team_generation_option.min_team_size
        while self.has_empty_teams() and k > 1:
            clique_student_lists = self.find_clique_teams(students, k)

            if not clique_student_lists:
                k -= 1
                continue

            if clique_student_lists:  # if cliques of size k are found
                empty_team = self.next_empty_team()
                self.add_best_clique_to_team(empty_team, clique_student_lists)
                if empty_team.size == team_generation_option.min_team_size:
                    empty_team.lock()

        self.increment_stage()

        # Step 3: fill fragments
        while self.get_remaining_students(students):
            largest_fragment_team = self.get_largest_available_team(team_generation_option)
            if largest_fragment_team is None:
                break

            while largest_fragment_team.size < team_generation_option.min_team_size:
                k = team_generation_option.min_team_size - largest_fragment_team.size
                all_cliques = self.find_lte_cliques(students, k)
                non_single_cliques = [clique for clique in all_cliques if len(clique) == 1]
                if len(non_single_cliques) < len(all_cliques):
                    # don't consider cliques of 1 unless there are only cliques of 1 returned
                    all_cliques = non_single_cliques
                self.add_best_clique_to_team(largest_fragment_team, all_cliques)

        self.increment_stage()

        # Step 4: place last students in the team best for them
        if self.get_remaining_students(students):
            _generate_with_choose(self, students, self.teams, team_generation_option)

        return teams

    def choose(self, teams, students):
        """
        A choose function selects a (team, student) pair where the student will be added to the team.
        This is used by _generate_with_choose() to fill team slots. In the social algorithm, this is the
        final step used to assign any remaining unassigned students.

        It chooses the smallest team and the best student student for that team, based on overall utility.
        Overall utility combines all 4 types of utility, and is defined in the weight algorithm.
        :param teams: the teams to choose from
        :param students: the students to choose from
        :return: Tuple[Team, Student] (smallest team, best student for that team)
        """
        if not teams or not students:
            return None, None

        smallest_team = teams[0]
        for team in teams:
            if team.size < smallest_team.size:
                smallest_team = team

        best_student, score = None, float('-inf')
        for student in students:
            curr_score = self._get_utility(smallest_team, student)
            if curr_score > score:
                score = curr_score
                best_student = student

        if not best_student:
            return None, None

        return smallest_team, best_student

    def get_largest_available_team(self, team_generation_option) -> Team:
        """
        Return the largest available team
        """
        largest_size = 0
        largest_available_team = None
        for team in self.get_available_teams(self.teams, team_generation_option):
            if team.size >= team_generation_option.min_team_size:
                continue
            if team.size > largest_size:
                largest_available_team = team
                largest_size = team.size
        return largest_available_team

    def find_clique_teams(self, students: [Student], size: int, clean: bool = False) -> List[List[Student]]:
        """
        Only students not in a team already are able to be placed in cliques. Allowing multi-memberships is an optional
        parameter.
        :param students: A list of all students (used to return a list of Student objects instead of ids)
        :param size: The size of clique to look for
        :param clean: When clean=True, multi-memberships are not allowed.
        :return: The cliques with the desired specifications
        """
        clique_ids = self.clique_finder.get_cliques(size)
        if clique_ids is None:
            return []
        clique_student_list = _clique_ids_to_student_list(students, clique_ids)
        if clean:
            clique_student_list = clean_clique_list(clique_student_list)
        return valid_clique_list(clique_student_list)

    def find_lte_cliques(self, students: [Student], size: int) -> List[List[Student]]:
        """
        Multi-memberships are allowed, all cliques of sizes [k...1] are included.
        Multi-membership means [1, 2, 3] and [2, 3, 4] can both be returned as elements in the outputted list, even
        though 2 nd 3 are in both cliques.
        Only students not in a team already are able to be placed in cliques.
        """
        clique_ids = self.clique_finder.find_cliques_lte_size(size)
        if clique_ids is None:
            return []
        clique_student_list = _clique_ids_to_student_list(students, clique_ids)
        return valid_clique_list(clique_student_list)

    def add_best_clique_to_team(self, team: Team, clique_student_lists: List[List[Student]]) -> bool:
        """
        Find the most suitable clique to add to team and add it.
        :return: Whether or not a clique was added to the team
        """
        if not clique_student_lists:
            return False

        best_clique = self.best_clique_for_team(team, clique_student_lists)
        if not best_clique:
            return False

        self.save_students_to_team(team, best_clique)
        return True

    def best_clique_for_team(self, team: Team, clique_student_lists: List[List[Student]]) -> List[Student]:
        best_clique, best_clique_score = None, float('-inf')
        for clique in clique_student_lists:
            score = team_suitability_score(team, clique)
            if score > best_clique_score:
                best_clique = clique
                best_clique_score = score
        return best_clique

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

        requirement_utility = get_requirement_utility(team, student)
        social_utility = get_social_utility(team, student)
        diversity_utility = get_diversity_utility(
            team, student,
            self.options.diversify_options,
            self.options.concentrate_options)
        preference_utility = get_preference_utility(
            team, student,
            self.options.max_project_preferences)

        return requirement_utility + social_utility + diversity_utility + preference_utility


def team_suitability_score(team: Team, student_list: List[Student]) -> float:
    if not student_list:
        return 0

    overall_utility = 0
    for student in student_list:
        overall_utility += get_social_utility(team, student)
    return overall_utility / len(student_list)  # TODO: improve scoring function?


def valid_clique_list(cliques: List[List[Student]]) -> List[List[Student]]:
    valid_cliques = [clique for clique in cliques if _clique_is_valid(clique)]
    return valid_cliques


def clean_clique_list(cliques: List[List[Student]]) -> List[List[Student]]:
    seen_students = []
    cleaned_cliques = []
    for clique in cliques:
        if any([student in seen_students for student in clique]):
            continue
        cleaned_cliques.append(clique)
        seen_students += clique
    return cleaned_cliques


def _clique_is_valid(clique: List[Student]) -> bool:
    """
    A valid clique in this context means a clique where all members are not already in teams
    """
    for student in clique:
        if student.is_added():
            return False
    return True


def _clique_ids_to_student_list(students: [Student], clique_ids: [int]) -> [[Student]]:
    cliques = []
    for clique in clique_ids:
        clique_students = [student for student in students if student.id in clique]
        cliques.append(clique_students)
    return cliques
