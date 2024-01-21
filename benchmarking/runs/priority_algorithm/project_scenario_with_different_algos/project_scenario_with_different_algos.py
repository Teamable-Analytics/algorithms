from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig, WeightAlgorithmConfig, \
    DoubleRoundRobinAlgorithmConfig
from api.models.enums import AlgorithmType
from api.models.student import Student
from api.models.team import TeamShell
from benchmarking.evaluations.metrics.average_project_requirements_coverage import AverageProjectRequirementsCoverage
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.project_scenario import ProjectScenario
from benchmarking.runs.interfaces import Run
from benchmarking.runs.priority_algorithm.project_scenario_with_different_algos.custom_student_provider import \
    CustomStudentProvider
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation_set import SimulationSetArtifact, SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


class ProjectScenarioWithDifferentAlgos(Run):
    MAX_KEEP = 50
    MAX_SPREAD = 50
    MAX_ITERATE = 500
    MAX_TIME = 1000000
    CLASS_SIZES = range(12, 1201, 24)

    def start(self, num_trials: int = 30, generate_graphs: bool = False):
        scenario = ProjectScenario()

        for class_size in self.CLASS_SIZES:
            print("CLASS SIZE /", class_size)
            student_provider = CustomStudentProvider(class_size)

            metrics = {
                "PrioritySatisfaction": PrioritySatisfaction(
                    goals_to_priorities(scenario.goals),
                    False,
                ),
                "AverageProjectRequirementsCoverage": AverageProjectRequirementsCoverage(),
            }

            artifact: SimulationSetArtifact = SimulationSet(
                settings=SimulationSettings(
                    num_teams=class_size // 4,
                    student_provider=student_provider,
                    scenario=scenario,
                    cache_key=f"priority_algorithm/project_scenario_with_different_algos/class_size_{class_size}",
                ),
                algorithm_set={
                    AlgorithmType.PRIORITY: [
                        PriorityAlgorithmConfig(
                            MAX_TIME=self.MAX_TIME,
                            MAX_KEEP=self.MAX_KEEP,
                            MAX_SPREAD=self.MAX_SPREAD,
                            MAX_ITERATE=self.MAX_ITERATE,
                            name="PriorityAlgorithm",
                        ),
                    ],
                    AlgorithmType.WEIGHT: [WeightAlgorithmConfig()],
                    AlgorithmType.DRR: [DoubleRoundRobinAlgorithmConfig(utility_function=additive_utility_function)],
                },
            ).run(num_runs=num_trials)


def additive_utility_function(student: Student, team: TeamShell) -> float:
    if len(team.requirements) == 0:
        return 0.0

    return sum(
        [
            student.meets_requirement(requirement)
            for requirement in team.requirements
        ]
    ) / float(len(team.requirements))


if __name__ == "__main__":
    ProjectScenarioWithDifferentAlgos().start()
