"""
Graph Representation:
dict with tuple keys
i.e. social_graph[(0, 1)] = FRIEND means that student 0 indicated friendship toward student 1

for a bidirectional graph, both values would just be the same in either direction so it wouldn't matter which we started with

when we reduce the social graph, edges are boolean values
"""
from itertools import combinations

from algorithm.social_algorithm.social_graph import SocialGraph
from student import Student

"""
levelled subgraph structure:
keys: int
values: [int]

i.e. the graph will implicitly be defined be a 'level' (like FF, FN, NN, etc) and student b's id is contained in 
     student a's list if a has a connection of 'level' or stronger to student b
     
e.g. {1: [2, 3], 2: [1, 3], 3: [1, 2]} means student 1 has 'level' or stronger connection to students 2 and 3
     these are undirected, so if student 2 is in student 1's list, the inverse must be true
"""


class CliqueFinder:
    def __init__(self, students: [Student], social_graph: SocialGraph):
        self._students = students
        self.social_graph = social_graph

    def is_clique(self, subgraph: dict) -> bool:
        # essentially check if this graph is complete
        member_ids = list(subgraph.keys())
        for member_id in member_ids:
            connected = [i for i in member_ids if i != member_id]
            if not connected == subgraph[member_id]:
                return False
        return True

    def get_cliques(self, size: int) -> [[int]]:
        cliques = self.find_cliques_of_size(size)
        return self.clean_cliques(cliques)

    def find_cliques_lte_size(self, size: int) -> [[int]]:
        all_cliques = []
        k = size
        while k > 0:
            all_cliques += self.find_cliques_of_size(k)
            k -= 1
        return all_cliques

    def find_cliques_of_size(self, size: int) -> [[int]]:
        if size == 1:
            return [[student.id] for student in self._students]

        # TODO: better algorithm? This one is O(n-choose-k)
        cliques = []  # [[int]]
        for members in combinations(self._students, size):
            member_ids = [student.id for student in members]
            subgraph = self.social_graph.subgraph(member_ids)
            if self.is_clique(subgraph):
                cliques.append(member_ids)
        return cliques

    def clean_cliques(self, cliques: [[int]]) -> [[int]]:
        """Clean means no conflicts. A student in one clique cannot be in another, but the normal algorithm doesn't
        enforce this restriction """

        """
        cliques = [
            [1, 2, 3]
            [3, 4, 5]
        ]
        """
        already_members = []
        cleaned_cliques = []
        for clique in cliques:
            if any([member in already_members for member in clique]):
                continue
            already_members += clique
            cleaned_cliques.append(clique)
        return cleaned_cliques
