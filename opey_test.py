from abc import ABC, abstractmethod, abstractstaticmethod
from collections import namedtuple
from typing import List

from restructure.models.enums import AlgorithmType


"""

todo: explain how a new attribute might be added to to the scenario/simulation module
    - change ScenarioAttribute
    - change data providers to populate that attribute
    
    
    
okay so for the whole "what is female" thing

Scenarios can be instanced instead of statically used.
Parameters include whichever things need to be known about them
A method @property returns their goals
So for example DiversifyGenderMin2Female(gender_value_for_female=2).goals
"""


class NumberOperation(ABC):
    @classmethod
    @abstractmethod
    def calculate(cls, numbers: List[int]):
        raise NotImplementedError


class SumNumbers(NumberOperation):

    @classmethod
    def calculate(cls, numbers):
        return sum(numbers)


class AverageNumbers(NumberOperation):

    @classmethod
    def calculate(cls, numbers: List[int]):
        return sum(numbers) / len(numbers)


if __name__ == "__main__":
    # nums = [1, 2, 3, 4, 5, 6, 7]
    # print(SumNumbers.calculate(nums))
    # print(AverageNumbers.calculate(nums))

    # outputs = {
    #     algorithm: [1, 3] for algorithm in AlgorithmType
    # }
    #
    # print(outputs)
    # print(outputs[AlgorithmType.RANDOM])

    # Student = namedtuple('Student', ['name', 'age', 'DOB'])
    # s1 = Student(
    #     blah="something"
    # )
    pass
