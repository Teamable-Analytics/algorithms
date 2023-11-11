from typing import cast, List, Tuple, Optional

from api.ai.interfaces.algorithm import ChooseAlgorithm
from api.ai.interfaces.algorithm_config import SocialAlgorithmConfig
from api.ai.interfaces.algorithm_options import (
    SocialAlgorithmOptions,
    WeightAlgorithmOptions,
)
from api.ai.social_algorithm.clique_finder import CliqueFinder
from api.ai.social_algorithm.custom_models import TeamWithCliques
from api.ai.social_algorithm.evaluation import TeamEvaluation
from api.ai.social_algorithm.social_graph import SocialGraph
from api.ai.social_algorithm.utils import (
    next_empty_team,
    has_empty_teams,
    clique_ids_to_student_list,
    valid_clique_list,
    clean_clique_list,
)
from api.ai.utils import save_students_to_team, generate_with_choose
from api.ai.weight_algorithm.utility import (
    get_social_utility,
    get_preference_utility,
)
from api.ai.weight_algorithm.weight_algorithm import WeightAlgorithm
from api.models.enums import Relationship
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet

DEFAULT_WEIGHT_ALGORITHM_CONFIG = SocialAlgorithmConfig()


class SocialAlgorithm(ChooseAlgorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_options: SocialAlgorithmOptions = cast(
            SocialAlgorithmOptions, self.algorithm_options
        )
        if self.algorithm_config:
            self.algorithm_config: SocialAlgorithmConfig = cast(
                SocialAlgorithmConfig, self.algorithm_config
            )
        else:
            self.algorithm_config = DEFAULT_WEIGHT_ALGORITHM_CONFIG

        self.teams: List[TeamWithCliques] = [
            TeamWithCliques.from_team(team) for team in self.teams
        ]

    def generate(self, students: List[Student]) -> TeamSet:
        # todo: accounting for locked/pre-set teams is a whole fiesta
        initially_locked_teams = [team for team in self.teams if team.is_locked]
        social_graph = SocialGraph(students, Relationship.FRIEND.value * 2)
        self.clique_finder = CliqueFinder(students, social_graph)
        # find all cliques of all sizes, so that they are cached for later
        self.clique_finder.find_cliques_lte_size(
            self.team_generation_options.max_team_size
        )

        # Step 1: Makes teams out of cliques of the correct team size
        clique_student_lists = self.find_clique_teams(
            students, self.team_generation_options.max_team_size, clean=True
        )
        for student_list in clique_student_lists:
            # todo: what if more cliques than team slots
            empty_team = next_empty_team(self.teams)
            if empty_team is None:
                break
            save_students_to_team(empty_team, student_list)
            empty_team.set_clique()
            empty_team.lock()

        # Step 2: fill extra team slots with fragments (largest fragments first)
        # todo: team of min size + random person? suboptimal
        k = self.team_generation_options.min_team_size
        while has_empty_teams(self.teams) and k > 1:
            clique_student_lists = self.find_clique_teams(students, k)

            if not clique_student_lists:
                k -= 1
                continue

            if clique_student_lists:  # if cliques of size k are found
                empty_team = next_empty_team(self.teams)
                self.add_best_clique_to_team(empty_team, clique_student_lists)
                if empty_team.size == self.team_generation_options.min_team_size:
                    empty_team.set_clique()
                    empty_team.lock()

        # Step 3: fill fragments
        while self.get_remaining_students(students):
            largest_fragment_team = self.get_largest_fragment_team(
                self.team_generation_options.min_team_size
            )
            if largest_fragment_team is None:
                break

            while (
                largest_fragment_team.size < self.team_generation_options.min_team_size
            ):
                # todo: favour min or max team size here?
                k = (
                    self.team_generation_options.min_team_size
                    - largest_fragment_team.size
                )
                all_cliques = self.find_lte_cliques(students, k)
                non_single_cliques = [
                    clique for clique in all_cliques if len(clique) == 1
                ]
                if len(non_single_cliques) < len(all_cliques):
                    # don't consider cliques of 1 unless there are only cliques of 1 returned
                    all_cliques = non_single_cliques
                self.add_best_clique_to_team(largest_fragment_team, all_cliques)

        # Step 4: place last students in the team best for them
        if self.get_remaining_students(students):
            generate_with_choose(self, students, self.teams)

        # (Pseudo) Step 5: Keep team compositions intact, but reassign teams so they better fit with project preferences
        if self.team_generation_options.initial_teams:
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
                for team in self.get_available_teams(self.teams):
                    if team.students:
                        # if the team has students, it has already been filled
                        continue
                    curr_score = self.team_suitability_score(
                        team, team_composition, use_project_preference=True
                    )
                    if curr_score >= best_score:
                        best_team = team
                        best_score = curr_score
                save_students_to_team(best_team, team_composition)

        return TeamSet(
            teams=[
                TeamWithCliques.to_team(team_with_cliques)
                for team_with_cliques in self.teams
            ]
        )

    def team_suitability_score(
        self,
        team: Team,
        student_list: List[Student],
        use_project_preference: bool = False,
    ) -> float:
        if not student_list:
            # todo: student_list should never be empty, handle this better?
            return float("-inf")

        overall_utility = 0
        if use_project_preference:
            for student in student_list:
                overall_utility += get_preference_utility(
                    team, student, self.algorithm_options.max_project_preferences
                )

        overall_utility += get_social_utility(team, student_list)
        # todo: replace with scoring function
        return overall_utility / len(student_list)

    def get_largest_fragment_team(self, min_team_size: int) -> Team:
        largest_size = 0
        largest_fragment = None
        for team in self.teams:
            if team.size >= min_team_size:
                continue
            if team.size > largest_size:
                largest_fragment = team
                largest_size = team.size
        # todo: what if this returns None
        return largest_fragment

    def find_clique_teams(
        self, students: List[Student], size: int, clean: bool = False
    ) -> List[List[Student]]:
        clique_ids = self.clique_finder.get_cliques(size)
        if clique_ids is None:
            return []
        clique_student_list = clique_ids_to_student_list(students, clique_ids)
        if clean:
            clique_student_list = clean_clique_list(clique_student_list)
        return valid_clique_list(clique_student_list)

    def find_lte_cliques(
        self, students: List[Student], size: int
    ) -> List[List[Student]]:
        """
        Multi-memberships are allowed, all cliques of sizes [k...1] are included
        """
        clique_ids = self.clique_finder.find_cliques_lte_size(size)
        if clique_ids is None:
            return []
        clique_student_list = clique_ids_to_student_list(students, clique_ids)
        return valid_clique_list(clique_student_list)

    def add_best_clique_to_team(
        self, team: Team, clique_student_lists: List[List[Student]]
    ) -> bool:
        if not clique_student_lists:
            return False

        best_clique = self.best_clique_for_team(team, clique_student_lists)
        if not best_clique:
            return False

        save_students_to_team(team, best_clique)
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

    def choose(
        self, teams: List[Team], students: List[Student]
    ) -> Tuple[Optional[Team], Optional[Student]]:
        """Choose the smallest team and the student that has the highest utility for that team"""
        smallest_team = None
        for team in teams:
            if smallest_team is None or team.size < smallest_team.size:
                smallest_team = team

        if not smallest_team:
            return None, None

        greatest_utility = 0
        greatest_utility_student = None
        for student in students:
            utility = WeightAlgorithm.get_utility(
                self.algorithm_options, smallest_team, student
            )
            if greatest_utility_student is None or utility > greatest_utility:
                greatest_utility = utility
                greatest_utility_student = student

        return smallest_team, greatest_utility_student


def weight_options_from_social_options(
    options: SocialAlgorithmOptions,
) -> WeightAlgorithmOptions:
    return WeightAlgorithmOptions(
        requirement_weight=options.requirement_weight,
        social_weight=options.social_weight,
        diversity_weight=options.diversity_weight,
        preference_weight=options.preference_weight,
        max_project_preferences=options.max_project_preferences,
        friend_behaviour=options.friend_behaviour,
        enemy_behaviour=options.enemy_behaviour,
        attributes_to_diversify=options.attributes_to_diversify,
        attributes_to_concentrate=options.attributes_to_concentrate,
    )
