import json
from json import JSONEncoder, JSONDecoder
from typing import Dict, Union

from api.models.enums import RequirementOperator
from api.models.project.project import ProjectRequirement


class ProjectRequirementSerializer(JSONEncoder, JSONDecoder):
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

    def decode(self, s, _w=...) -> ProjectRequirement:
        data = json.loads(s)
        return ProjectRequirement(
            attribute=data["attribute"],
            operator=RequirementOperator(data["operator"]),
            value=data["value"],
        )
