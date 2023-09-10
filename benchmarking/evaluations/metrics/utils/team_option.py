from benchmarking.evaluations.metrics.utils.team_calculations import *


class TeamOption:
    strict_mode: bool
    friend_mode: bool
    is_all_happy: bool

    def __init__(self, strict_mode: bool = True, friend_mode: bool = True, is_strictly_happy: bool = True,
                 is_all_happy: bool = True):
        self.strict_mode = strict_mode
        self.friend_mode = friend_mode
        self.is_strictly_happy = is_strictly_happy
        self.is_all_happy = is_all_happy

    def get_function(self):

        if self.strict_mode and self.friend_mode:
            return is_strictly_happy_team_friend
        if self.strict_mode and not self.friend_mode:
            return is_strictly_happy_team_enemy

        if self.friend_mode and self.is_strictly_happy and self.is_all_happy:
            return is_happy_team_allshp_friend
        if self.friend_mode and self.is_strictly_happy and not self.is_all_happy:
            return is_happy_team_1shp_friend
        if self.friend_mode and not self.is_strictly_happy and self.is_all_happy:
            return is_happy_team_allhp_friend
        if self.friend_mode and not self.is_strictly_happy and not self.is_all_happy:
            return is_happy_team_1hp_friend

        if self.is_strictly_happy and self.is_all_happy:
            return is_happy_team_allshp_enemy
        if self.is_strictly_happy and not self.is_all_happy:
            return is_happy_team_1shp_enemy
        if not self.is_strictly_happy and self.is_all_happy:
            return is_happy_team_allhp_enemy
        if not self.is_strictly_happy and not self.is_all_happy:
            return is_happy_team_1hp_enemy
