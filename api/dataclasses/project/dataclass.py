from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, Optional

from api.dataclasses.enums import RequirementOperator, RequirementsCriteria

if TYPE_CHECKING:
    from api.dataclasses.student import Student


@dataclass
class ProjectRequirement:
    attribute: int
    operator: RequirementOperator
    value: int
    criteria: RequirementsCriteria = RequirementsCriteria.SOMEONE
    num_members_meeting: Optional[int] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if (
            self.criteria == RequirementsCriteria.N_MEMBERS
            and self.num_members_meeting is None
        ):
            raise ValueError(
                "'num_members_meeting' is required when using RequirementsCriteria.N_MEMBERS"
            )
        if (
            self.criteria != RequirementsCriteria.N_MEMBERS
            and self.num_members_meeting is not None
        ):
            print(
                "[WARNING]:'num_members_meeting' has no effect when not using RequirementsCriteria.N_MEMBERS"
            )

    def met_by_student(self, student: "Student") -> bool:
        """
        Ignoring the criteria of this requirement, just if a student meets it or not
        """
        is_met = False
        # note that attributes are modelled as lists of integers
        for value in student.attributes.get(self.attribute, []):
            if self.operator == RequirementOperator.LESS_THAN:
                is_met |= value < self.value
            elif self.operator == RequirementOperator.MORE_THAN:
                is_met |= value > self.value
            else:  # default case is RequirementOperator.EXACTLY
                is_met |= value == self.value
        return is_met

    def satisfaction_by_students(self, students: List["Student"]) -> float:
        """
        Calculates how satisfied a requirement is by an arbitrary group of students,
        factoring in the requirement's criteria
        """
        num_members_meeting_requirement = len(
            [s for s in students if self.met_by_student(s)]
        )

        if self.criteria == RequirementsCriteria.SOMEONE:
            return 1 if num_members_meeting_requirement > 0 else 0
        if self.criteria == RequirementsCriteria.EVERYONE:
            return num_members_meeting_requirement / len(students)
        if self.criteria == RequirementsCriteria.N_MEMBERS:
            return min(num_members_meeting_requirement / self.num_members_meeting, 1)


@dataclass
class Project:
    _id: int
    name: str = None
    # if multiple teams can work on this project. specified here
    number_of_teams: int = 1
    requirements: List[ProjectRequirement] = field(default_factory=list)

    @property
    def id(self) -> int:
        return self._id
