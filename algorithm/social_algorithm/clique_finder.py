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
    """
    Change approach to find all cliques of sizes [1...k] at once and store them in a hash table
    """
    cliques = {
        # size: [[Student]]
    }

    def __init__(self, students: [Student], social_graph: SocialGraph):
        self._students = students
        self.social_graph = social_graph
        self.cliques = {
            # a clique of size 1 is simply just the student
            1: [{student.id} for student in self._students]
        }

    def is_clique(self, subgraph: dict) -> bool:
        # essentially check if this graph is complete
        member_ids = list(subgraph.keys())
        for member_id in member_ids:
            connected = [i for i in member_ids if i != member_id]
            if not connected == subgraph[member_id]:
                return False
        return True

    def get_cliques(self, size: int) -> [[int]]:
        if size in self.cliques:
            return self.cliques[size]

        for k, cliques in self.find_cliques_of_size(size):
            self.cliques[k] = cliques
            if k == size:
                return cliques

    def find_cliques_lte_size(self, size: int) -> [[int]]:
        all_cliques = []
        k = size
        while k > 0:
            all_cliques += self.get_cliques(k)
            k -= 1
        return all_cliques

    def find_cliques_of_size(self, size: int) -> [[int]]:
        # Adapted from https://iq.opengenus.org/algorithm-to-find-cliques-of-a-given-size-k/
        k = 2
        cliques = [{from_id, to_id} for from_id, to_id in self.social_graph.edges() if from_id != to_id]
        while cliques:
            # result
            yield k, cliques
            # merge k-cliques into (k+1)-cliques
            cliques_1 = set()
            for u, v in combinations(cliques, 2):
                w = u ^ v
                if len(w) == 2 and self.social_graph.has_edge(*w):
                    cliques_1.add(tuple(u | w))
            # remove duplicates
            cliques = list(map(set, cliques_1))
            k += 1
