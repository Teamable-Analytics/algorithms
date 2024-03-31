from benchmarking.evaluations.metrics.cosine_similarity import AverageCosineDifference
from benchmarking.simulation.simulation_set import SimulationSetArtifact


def calculate_inter_homogeneity_score(artifacts: SimulationSetArtifact, scenario_attribute_value: int):
    # Calculate Inter-Homogeneity from stdev of cosine difference
    for algorithm_name, (team_sets, run_times) in artifacts.items():
        cosine_diffs = []
        for team_set in team_sets:
            cosine_diffs.append(
                AverageCosineDifference(
                    [scenario_attribute_value]
                ).calculate_stdev(team_set)
            )
        print(f",{sum(cosine_diffs) / len(cosine_diffs)}", end="")
    print()
