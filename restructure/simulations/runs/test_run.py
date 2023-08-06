from restructure.models.enums import ScenarioAttribute, RequirementType
from restructure.models.project import Project, ProjectRequirement
from restructure.simulations.data_service.interfaces import MockStudentProviderSettings
from restructure.simulations.data_service.simulated_data.mock_student_provider import (
    MockStudentProvider,
)
from restructure.simulations.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from restructure.simulations.evaluations.scenarios.diversify_gender import (
    ScenarioDiversifyGender,
)
from restructure.simulations.evaluations.scenarios.diversify_gender_min_2_female import (
    ScenarioDiversifyGenderMin2Female,
)
from restructure.simulations.simulation_service.simulation import Simulation

if __name__ == "__main__":
    class_sizes = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    # average_gini_indexes = []

    PROJECT_REQUIREMENT_VALUE = 1

    """
    introduce concept of a project config
    """
    projects = [
        Project(
            _id=proj_id,
            requirements=[
                ProjectRequirement(
                    attribute=100 + req_id,
                    operator=RequirementType.EXACTLY,
                    value=PROJECT_REQUIREMENT_VALUE,
                ) for req_id in range(0, 8)
            ],
        ) for proj_id in range(0, 7)
    ]

    for class_size in class_sizes:
        data_settings = MockStudentProviderSettings(
            num_students=class_size,
            num_friends_per_student=10,
            num_attributes=10,
        )
        simulation_outputs = Simulation(
            scenario=ScenarioDiversifyGenderMin2Female(value_of_female=2),
            student_provider=MockStudentProvider(data_settings),
            metric=AverageGiniIndex(),
        ).run(num_runs=1000)
        # average_gini_indexes.append()

        # GRAPH
