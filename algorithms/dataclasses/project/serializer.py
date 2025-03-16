from json import JSONEncoder
from typing import Dict, Union, Any

from algorithms.dataclasses.enums import RequirementOperator
from algorithms.dataclasses.project import ProjectRequirement
from algorithms.dataclasses.interfaces import DataClassDecoder


class ProjectRequirementSerializer(JSONEncoder, DataClassDecoder):
    def default(
        self, project_requirement: ProjectRequirement
    ) -> Dict[str, Union[int, str]]:
        if not isinstance(project_requirement, ProjectRequirement):
            raise TypeError("Object is not a project instance.")
        return {
            "attribute": project_requirement.attribute,
            "operator": project_requirement.operator.value,
            "value": project_requirement.value,
        }

    def decode(self, json_dict: Dict[str, Any]) -> ProjectRequirement:
        return ProjectRequirement(
            attribute=json_dict["attribute"],
            operator=RequirementOperator(json_dict["operator"]),
            value=json_dict["value"],
        )
