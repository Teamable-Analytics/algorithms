from restructure.simulations.data_service.interfaces import MockStudentProviderSettings
from restructure.simulations.data_service.simulated_data.mock_student_provider import (
    MockStudentProvider,
)
from restructure.simulations.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from restructure.simulations.evaluations.scenarios.diversify_gender_min_2_female import (
    ScenarioDiversifyGenderMin2Female,
)
from restructure.simulations.simulation_service.simulation import Simulation

if __name__ == "__main__":
    class_sizes = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    # average_gini_indexes = []

    PROJECT_REQUIREMENT_VALUE = 1

    for class_size in class_sizes:
        data_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            number_of_friends=10,
        )
        simulation_outputs = Simulation(
            scenario=ScenarioDiversifyGenderMin2Female(value_of_female=2),
            student_provider=MockStudentProvider(data_settings),
            metric=AverageGiniIndex(),
        ).run(num_runs=1000)
        # average_gini_indexes.append()

        # GRAPH
