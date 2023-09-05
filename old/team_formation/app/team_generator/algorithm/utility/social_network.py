from old.team_formation.app.team_generator.algorithm.consts import (
    DEFAULT,
    FRIEND,
    ENEMY,
    LOW_WEIGHT,
    HIGH_WEIGHT,
)


class SocialNetwork:
    _network = {}

    def __init__(self, students, balanced=True):
        """
        WARNING: Passing an unbalanced social network to SubSocialNetwork causes inconsistencies in its methods.
        The ability to do this is currently only used for testing purposes.
        """
        self._network = self._create_social_network(students)
        if balanced:
            self._network = self._balance_network(self._network)

    def get_network(self):
        return self._network

    def get_weight(self, src, dest):
        if src not in self._network or dest not in self._network[src]:
            raise Exception(
                f"An edge from Student ({src}) to Student ({dest}) could not be found in the social network"
            )
        if src == dest:
            return DEFAULT
        return self._network[src][dest]

    def get_diameter(self):
        """
        Return the diameter of this network.
        Diameter defined in nested method.
        """
        return _calculate_network_diameter(self._network)

    def _create_social_network(self, students):
        social_network = {}
        for student in students:
            student_network = {}
            for other in students:
                if other.id in student.relationships:
                    student_network[other.id] = student.relationships[other.id]
                else:
                    student_network[other.id] = DEFAULT
            social_network[student.id] = student_network
        return social_network

    def _balance_network(self, network):
        """
        Balances the weights in a social network graph. Each edge will have the same weight in both directions,
        and this weight is calculated by the sum of the weights in either direction between any given pair of students
        """
        student_ids = list(network)
        new_network = {s: {} for s in student_ids}
        for s in student_ids:
            for other in student_ids:
                if other == s:
                    new_network[s][other] = new_network[other][s] = 0
                else:
                    combined_weight = network[s][other] + network[other][s]
                    new_network[s][other] = new_network[other][s] = _normalize_weight(
                        combined_weight
                    )
        return new_network


def _normalize_weight(combined_weight):
    # this is the theoretical max/min that any combined weight could be
    theo_max = 2 * ENEMY
    theo_min = 2 * FRIEND

    n = (combined_weight - theo_min) / (theo_max - theo_min)
    # place in the range of [LOW_VALUE, HIGH_VALUE]
    normalized_weight = LOW_WEIGHT + ((HIGH_WEIGHT - LOW_WEIGHT) * n)
    return normalized_weight


def _calculate_network_diameter(network):
    """
    Calculates the diameter of this network.

    Diameter is defined as the largest path cost from the set:
        { shortest path's cost for each unique pair of student in the social network }
    """
    student_ids = list(network)
    diameter = LOW_WEIGHT
    if len(student_ids) < 2:
        return diameter

    distances = _setup_distances(student_ids)
    visited = []  # this is used to ensure we only retrieve unique pairs of students
    for s in student_ids:
        visited.append(s)
        for other in student_ids:
            if other in visited:
                continue
            else:
                path_cost = _shortest_path_cost(s, other, network, distances)
                diameter = path_cost if path_cost > diameter else diameter

    return diameter


def _shortest_path_cost(src, dest, network, distances):
    """
    Calculates and/or returns the minimum path cost to traverse from src to dest in the network graph.
    Also populates the shortest path cost from src to every other node in the network and stores those values.
    Implementation is specific to this case and only used in _calculate_network_diameter().
    """
    if distances[src][dest] < float("inf"):
        return distances[src][dest]  # min cost has already been calculated

    student_ids = list(network)
    queue = [s for s in student_ids]

    while len(queue) > 0:
        student = _pop(queue, distances[src])

        for other in student_ids:
            if student == other:
                continue

            temp = distances[src][student] + network[student][other]
            distances[src][other] = (
                temp if temp < distances[src][other] else distances[src][other]
            )
            distances[other][src] = distances[src][other]

    return distances[src][dest]


def _setup_distances(student_ids):
    """
    Set up the distances dictionary storing distances between nodes in the graph
    """
    distances = {s: {other: float("inf") for other in student_ids} for s in student_ids}
    for s in student_ids:
        distances[s][s] = 0  # distances to themselves are initialized to 0

    return distances


def _pop(q, dist):
    """
    Returns and removes from list the student id with the minimum dist as defined in the dist list.
    """
    min_dist_student = None
    min_dist = float("inf")
    for s_id in q:
        changed = dist[s_id] < min_dist
        min_dist = dist[s_id] if changed else min_dist
        min_dist_student = s_id if changed else min_dist_student

    q.remove(min_dist_student)
    return min_dist_student
