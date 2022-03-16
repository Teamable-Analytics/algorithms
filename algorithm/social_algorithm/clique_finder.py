"""
Graph Representation:
dict with tuple keys
i.e. social_graph[(0, 1)] = FRIEND means that student 0 indicated friendship toward student 1

for a bidirectional graph, both values would just be the same in either direction so it wouldn't matter which we started with

when we reduce the social graph, edges are boolean values
"""
from algorithm.social_algorithm.social_graph import SocialGraph


class CliqueFinder:
    def __init__(self):
        pass

    def is_clique(self, social_graph: SocialGraph, member_ids: [int]) -> bool:
        # graph is bidirectional at this point
        for member, index in enumerate(member_ids):
            for j in range(index + 1, len(member_ids)):
                other_member = member_ids[j]
                if not social_graph.edge_exists(member, other_member):
                    return False
        return True

    def get_cliques(self, i, l, size: int) -> [[int]]:
        cliques = self.find_cliques(i, l, size)
        return self.clean_cliques(cliques)

    def find_cliques(self, i, l, size: int) -> [[int]]:
        # TODO: find all then return one, check it's not in

        # if degree is sufficient
        pass

    def clean_cliques(self, cliques: [[int]]) -> [[int]]:
        """Clean means no conflicts. A student in one clique cannot be in another, but the normal algorithm doesn't
        enforce this restriction """
        already_members = []
        cleaned_cliques = []
        for clique in cliques:
            if any([member in already_members for member in clique]):
                continue
            already_members += clique
            cleaned_cliques.append(clique)
        return cleaned_cliques