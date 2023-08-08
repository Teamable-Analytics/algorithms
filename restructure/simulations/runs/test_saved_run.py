import math

from restructure.models.enums import ScenarioAttribute
from restructure.simulations.data.interfaces import MockStudentProviderSettings
from restructure.simulations.data.simulated_data.mock_student_provider import (
    MockStudentProvider,
)
from restructure.simulations.evaluations.metrics.average_gini_index import (
    AverageGiniIndex,
)
from restructure.simulations.evaluations.scenarios.diversify_gender_min_2_female import (
    ScenarioDiversifyGenderMin2Female,
)
from restructure.simulations.simulation.simulation import Simulation


def test_saved_run():
    """
    Goal: Run diversify gender scenario, measure average gini index
    """

    # Defining our changing x-values (in the graph sense)
    class_sizes = [100, 150, 200, 250, 300]

    MALE = 1
    FEMALE = 2

    for class_size in class_sizes:
        print("CLASS SIZE /", class_size)
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [(MALE, 0.5), (FEMALE, 0.5)]
            },
        )
        simulation_outputs = Simulation(
            num_teams=math.ceil(class_size / 5),
            scenario=ScenarioDiversifyGenderMin2Female(value_of_female=FEMALE),
            student_provider=MockStudentProvider(student_provider_settings),
            metric=AverageGiniIndex(attribute=ScenarioAttribute.GENDER.value),
        ).run(num_runs=100)

        # print(simulation_outputs)
        print("=>", Simulation.average_metric(simulation_outputs))
