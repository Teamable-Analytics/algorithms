from dataclasses import dataclass

from algorithms.dataclasses.team import Team


@dataclass
class TeamWithCliques(Team):
    is_clique: bool = False

    @classmethod
    def from_team(cls, team: Team) -> "TeamWithCliques":
        return cls(
            _id=team.id,
            name=team.name,
            project_id=team.project_id,
            requirements=team.requirements,
            is_locked=team.is_locked,
            students=team.students,
        )

    @classmethod
    def to_team(cls, team_with_clique: "TeamWithCliques") -> Team:
        return Team(
            _id=team_with_clique.id,
            name=team_with_clique.name,
            project_id=team_with_clique.project_id,
            requirements=team_with_clique.requirements,
            is_locked=team_with_clique.is_locked,
            students=team_with_clique.students,
        )

    def set_clique(self):
        self.is_clique = True
