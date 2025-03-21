from itertools import combinations
from typing import List, Set, Tuple

from algorithms.ai.social_algorithm.social_graph import SocialGraph
from algorithms.dataclasses.student import Student


class CliqueFinder:
    """
    Find all cliques of sizes [1...k] at once and store them in a hash table.
    When find_cliques(k) is called, calculate cliques of sizes [1...k] and save the results as you go
    """

    def __init__(self, students: List[Student], social_graph: SocialGraph):
        self._students = students
        self.social_graph = social_graph
        self.cliques = {
            # a clique of size 1 is simply just the student
            1: [{student.id} for student in self._students]
        }

    def get_cliques(self, size: int) -> List[Set[int]]:
        if size in self.cliques:
            return self.cliques[size]  # return saved cliques if already computed

        for k, cliques in self.find_cliques():
            self.cliques[k] = cliques
            if k == size:
                return cliques

        self.cliques[size] = []
        return []

    def find_cliques_lte_size(self, size: int) -> List[Set[int]]:
        all_cliques = []
        k = size
        while k > 0:
            all_cliques += self.get_cliques(k)
            k -= 1
        return all_cliques

    def find_cliques(self) -> Tuple[int, List[Set[int]]]:
        # Adapted from https://iq.opengenus.org/algorithm-to-find-cliques-of-a-given-size-k/
        k = 2
        cliques = [
            {from_id, to_id}
            for from_id, to_id in self.social_graph.edges()
            if from_id != to_id
        ]
        while cliques:
            # result
            yield k, cliques  # https://realpython.com/introduction-to-python-generators/
            # merge k-cliques into (k+1)-cliques
            cliques_1 = set()
            for u, v in combinations(cliques, 2):
                w = u ^ v
                if len(w) == 2 and self.social_graph.has_edge(*w):
                    cliques_1.add(tuple(u | w))
            # remove duplicates
            cliques = list(map(set, cliques_1))
            k += 1
