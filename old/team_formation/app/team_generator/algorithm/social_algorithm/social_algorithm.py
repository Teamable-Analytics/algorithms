from typing import List

from old.team_formation.app.team_generator.algorithm.algorithms import (
    _generate_with_choose,
    WeightAlgorithm,
)
from old.team_formation.app.team_generator.algorithm.consts import FRIEND
from old.team_formation.app.team_generator.algorithm.evaluation import TeamEvaluation
from old.team_formation.app.team_generator.algorithm.social_algorithm.clique_finder import (
    CliqueFinder,
)
from old.team_formation.app.team_generator.algorithm.social_algorithm.social_graph import (
    SocialGraph,
)
from old.team_formation.app.team_generator.algorithm.utility import (
    get_social_utility,
    get_preference_utility,
)
from old.team_formation.app.team_generator.student import Student
from old.team_formation.app.team_generator.team import Team


class SocialAlgorithm(WeightAlgorithm):
    def __init__(self, algorithm_options, logger=None, *args, **kwargs):
        super().__init__(algorithm_options, logger)
        self.clique_finder = None
        self.set_default_weights()

    def set_default_weights(self):
        self.options.diversity_weight = 1
        self.options.preference_weight = (
            0  # we assign projects at the end with this algorithm
        )
        self.options.requirement_weight = 1
        self.options.social_weight = 1

    def generate(
        self, students: List[Student], teams: List[Team], team_generation_option
    ) -> List[Team]:
        # TODO: accounting for locked/pre-set teams is a whole fiesta
        self.teams = teams
        initially_locked_teams = [team for team in self.teams if team.is_locked]
        social_graph = SocialGraph(students, FRIEND * 2)
        self.clique_finder = CliqueFinder(students, social_graph)
        # find all cliques of all sizes, so that they are cached for later
        self.clique_finder.find_cliques_lte_size(team_generation_option.max_teams_size)

        # Step 1: Makes teams out of cliques of the correct team size
        clique_student_lists = self.find_clique_teams(
            students, team_generation_option.max_teams_size, clean=True
        )
        for student_list in clique_student_lists:
            empty_team = (
                self.next_empty_team()
            )  # TODO: what if more cliques than team slots
            if empty_team is None:
                break
            self.save_students_to_team(empty_team, student_list)
            empty_team.set_clique()
            empty_team.lock()

        self.increment_stage()

        # Step 2: fill extra team slots with fragments (largest fragments first)
        k = (
            team_generation_option.min_team_size
        )  # TODO: team of min size + random person? suboptimal
        while self.has_empty_teams() and k > 1:
            clique_student_lists = self.find_clique_teams(students, k)

            if not clique_student_lists:
                k -= 1
                continue

            if clique_student_lists:  # if cliques of size k are found
                empty_team = self.next_empty_team()
                self.add_best_clique_to_team(empty_team, clique_student_lists)
                if empty_team.size == team_generation_option.min_team_size:
                    empty_team.set_clique()
                    empty_team.lock()

        self.increment_stage()

        # Step 3: fill fragments
        while self.get_remaining_students(students):
            largest_fragment_team = self.get_largest_fragment_team(
                team_generation_option
            )
            if largest_fragment_team is None:
                break

            while largest_fragment_team.size < team_generation_option.min_team_size:
                # TODO: favour min or max team size here?
                k = team_generation_option.min_team_size - largest_fragment_team.size
                all_cliques = self.find_lte_cliques(students, k)
                non_single_cliques = [
                    clique for clique in all_cliques if len(clique) == 1
                ]
                if len(non_single_cliques) < len(all_cliques):
                    # don't consider cliques of 1 unless there are only cliques of 1 returned
                    all_cliques = non_single_cliques
                self.add_best_clique_to_team(largest_fragment_team, all_cliques)

        self.increment_stage()

        # Step 4: place last students in the team best for them
        if self.get_remaining_students(students):
            _generate_with_choose(self, students, self.teams, team_generation_option)

        self.increment_stage()

        # (Pseudo) Step 5: Keep team compositions intact, but reassign teams so they better fit with project preferences
        if team_generation_option.team_options:
            # if a project set was attached and students could have preferences for projects (which correlate to teams)
            # Step 5.1: Sort teams by best social scores first so those teams get their preferred projects
            team_evaluation = TeamEvaluation(self.teams)
            self.teams = sorted(
                self.teams, key=lambda team: team_evaluation.team_satisfaction(team)
            )
            # Step 5.2: Save team compositions
            team_compositions: List[List[Student]] = [
                team.students for team in self.teams
            ]
            # Step 5.3: Empty all teams
            for team in self.teams:
                if team not in initially_locked_teams:
                    team.empty()
                    team.unlock()
            # Step 5.4: Assign team compositions to Teams, according to project preferences
            for team_composition in team_compositions:
                # Note: By construction, organized teams are favoured in assigning preferred projects
                best_team, best_score = None, float("-inf")
                for team in self.get_available_teams(
                    self.teams, team_generation_option
                ):
                    if team.students:
                        # if the team has students, it has already been filled
                        continue
                    curr_score = self.team_suitability_score(
                        team, team_composition, use_project_preference=True
                    )
                    if curr_score >= best_score:
                        best_team = team
                        best_score = curr_score
                self.save_students_to_team(best_team, team_composition)

        return teams

    def team_suitability_score(
        self,
        team: Team,
        student_list: List[Student],
        use_project_preference: bool = False,
    ) -> float:
        if not student_list:
            return float("-inf")  # cannot be empty TODO: do properly

        overall_utility = 0
        if use_project_preference:
            for student in student_list:
                overall_utility += get_preference_utility(
                    team, student, self.options.max_project_preferences
                )

        overall_utility += get_social_utility(team, student_list)
        return overall_utility / len(
            student_list
        )  # TODO: replace with scoring function

    def get_largest_fragment_team(self, team_generation_option) -> Team:
        largest_size = 0
        largest_fragment = None
        for team in self.teams:
            if team.size >= team_generation_option.min_team_size:
                continue
            if team.size > largest_size:
                largest_fragment = team
                largest_size = team.size
        return largest_fragment  # TODO: what if this returns None

    def find_clique_teams(
        self, students: List[Student], size: int, clean: bool = False
    ) -> List[List[Student]]:
        clique_ids = self.clique_finder.get_cliques(size)
        if clique_ids is None:
            return []
        clique_student_list = self._clique_ids_to_student_list(students, clique_ids)
        if clean:
            clique_student_list = self.clean_clique_list(clique_student_list)
        return self.valid_clique_list(clique_student_list)

    def find_lte_cliques(
        self, students: List[Student], size: int
    ) -> List[List[Student]]:
        """
        Multi-memberships are allowed, all cliques of sizes [k...1] are included
        """
        clique_ids = self.clique_finder.find_cliques_lte_size(size)
        if clique_ids is None:
            return []
        clique_student_list = self._clique_ids_to_student_list(students, clique_ids)
        return self.valid_clique_list(clique_student_list)

    def valid_clique_list(self, cliques: List[List[Student]]) -> List[List[Student]]:
        valid_cliques = [clique for clique in cliques if self._clique_is_valid(clique)]
        return valid_cliques

    def clean_clique_list(self, cliques: List[List[Student]]) -> List[List[Student]]:
        seen_students = []
        cleaned_cliques = []
        for clique in cliques:
            if any([student in seen_students for student in clique]):
                continue
            cleaned_cliques.append(clique)
            seen_students += clique
        return cleaned_cliques

    def add_best_clique_to_team(
        self, team: Team, clique_student_lists: List[List[Student]]
    ) -> bool:
        if not clique_student_lists:
            return False

        best_clique = self.best_clique_for_team(team, clique_student_lists)
        if not best_clique:
            return False

        self.save_students_to_team(team, best_clique)
        return True

    def best_clique_for_team(
        self, team: Team, clique_student_lists: List[List[Student]]
    ) -> List[Student]:
        best_clique, best_clique_score = None, float("-inf")
        for clique in clique_student_lists:
            score = self.team_suitability_score(team, clique)
            if score > best_clique_score:
                best_clique = clique
                best_clique_score = score
        return best_clique

    def _clique_is_valid(self, clique: List[Student]) -> bool:
        """
        A valid clique in this context means a clique where all members are not already in teams
        """
        for student in clique:
            if student.is_added():
                return False
        return True

    def _clique_ids_to_student_list(
        self, students: List[Student], clique_ids: [int]
    ) -> List[List[Student]]:
        cliques = []
        for clique in clique_ids:
            clique_students = [student for student in students if student.id in clique]
            cliques.append(clique_students)
        return cliques
