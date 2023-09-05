class DataLoaderException(Exception):
    pass


class DataLoader:
    """Mock data loader"""

    def get_algorithm(self):
        pass

    def get_students_with_updated_relationships(
        self,
        course_id,
        section_ids,
        survey_id,
        algorithm_options,
        excluded_students_ids=None,
    ):
        pass

    def get_team_generation_options(self):
        pass

    def get_teams_from_excluded_teams(
        self, excluded_team_ids, students, team_generation_options
    ):
        pass
