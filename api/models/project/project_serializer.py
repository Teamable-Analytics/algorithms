import json
from typing import Dict

from api.models.project.project import ProjectRequirement


class ProjectRequirementSerializer(json.JSONEncoder, json.JSONDecoder):
    def default(self, project_requirement: ProjectRequirement) -> Dict[str, int]:
        if not isinstance(project_requirement, ProjectRequirement):
            raise TypeError("Object is not a project instance.")
        return {
            "attribute": project_requirement.attribute,
            "operator": project_requirement.operator.value,
            "value": project_requirement.value
        }
