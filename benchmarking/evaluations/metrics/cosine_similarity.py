import itertools
import statistics
from typing import List, Dict, Union, Tuple

from numpy import dot
from numpy.linalg import norm

from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.evaluations.interfaces import TeamSetMetric


class ClassAttributeSet:
    def __init__(self, team_set: TeamSet):
        # Dict of a (Attribute type, attribute value) to index of that combination in the vector used for cosine similarity
        self._data: Dict[Tuple[int, int], int] = {}
        index = 0
        for team in team_set.teams:
            for student in team.students:
                for key, values in student.attributes.items():
                    for value in values:
                        attribute = (key, value)
                        if attribute not in self._data:
                            self._data[attribute] = index
                            index += 1

    def index_of(self, attribute: Tuple[int, int]) -> int:
        return self._data.get(attribute)

    def size(self) -> int:
        return len(self._data)

    def get_student_vector(self, student: Student) -> List[int]:
        v = [0] * self.size()
        for key, values in student.attributes.items():
            for value in values:
                v[self.index_of((key, value))] = 1
        return v


class AverageCosineSimilarity(TeamSetMetric):
    def calculate(self, team_set: TeamSet) -> float:
        class_attributes = ClassAttributeSet(team_set)

        similarities = team_cosine_similarities(team_set.teams, class_attributes)

        return statistics.mean(similarities)

    @staticmethod
    def calculate_stdev(team_set: TeamSet) -> float:
        class_attributes = ClassAttributeSet(team_set)

        similarities = team_cosine_similarities(team_set.teams, class_attributes)

        return statistics.stdev(similarities)


def team_cosine_similarities(
    teams: List[Team], class_attributes: ClassAttributeSet
) -> List[float]:
    similarities = []
    for team in teams:
        if len(team.students) <= 0:
            continue
        total = 0
        num = 0
        for s1, s2 in itertools.combinations(team.students, 2):
            s1_vector = class_attributes.get_student_vector(s1)
            s2_vector = class_attributes.get_student_vector(s2)
            total += cosine_similarity(s1_vector, s2_vector)
            num += 1
        team_avg = total / num
        similarities.append(team_avg)
    return similarities


def cosine_similarity(
    v1: List[Union[int, float]], v2: List[Union[int, float]]
) -> float:
    """
    Can return a number between 0 and the length of the vectors
    """
    if len(v1) != len(v2):
        raise ValueError("Vectors must be the same length")
    if len(v1) == 0 or len(v2) == 0:
        raise ValueError("Vectors must not be empty")
    return dot(v1, v2) / (norm(v1) * norm(v2))
