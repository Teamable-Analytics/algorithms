import csv
import random
from typing import List

import pandas as pd
from matplotlib import pyplot as plt

from api.ai.interfaces.algorithm_config import PriorityAlgorithmConfig
from api.ai.interfaces.algorithm_options import PriorityAlgorithmOptions
from api.ai.interfaces.team_generation_options import TeamGenerationOptions
from api.ai.priority_algorithm.priority_algorithm import PriorityAlgorithm
from api.models.enums import ScenarioAttribute, Gender, Race, fromAlRaceToRace, fromAlGenderToGender, fromRaceToAlRace, \
    fromGenderToAlGender, fromYearLevelToAlYearLevel, fromNumbersToTimeSlots, AlgorithmType, fromAlYearLevelToYearLevel, \
    fromTimeslotsToNumbers
from api.models.student import Student
from api.models.team import Team
from api.models.team_set import TeamSet
from benchmarking.data.interfaces import StudentProvider
from benchmarking.data.simulated_data.mock_student_provider import MockStudentProviderSettings, MockStudentProvider
from benchmarking.evaluations.metrics.priority_satisfaction import PrioritySatisfaction
from benchmarking.evaluations.scenarios.concentrate_time_availability_and_diversify_gender_min_2_female import \
    ConcentrateTimeAvailabilityDiversifyGenderMin2Female
from benchmarking.evaluations.scenarios.diversify_gender_min_2_female import DiversifyGenderMin2Female
from benchmarking.simulation.goal_to_priority import goals_to_priorities
from benchmarking.simulation.simulation import Simulation
from benchmarking.simulation.simulation_set import SimulationSet
from benchmarking.simulation.simulation_settings import SimulationSettings


def generate_data():
    for idx in range(1000):
        class_size = 100
        student_provider_settings = MockStudentProviderSettings(
            number_of_students=class_size,
            attribute_ranges={
                ScenarioAttribute.GENDER.value: [
                    (Gender.MALE, 0.7),
                    (Gender.FEMALE, 0.2),
                    (Gender.OTHER, 0.1),
                ],
                ScenarioAttribute.RACE.value: [
                    (Race.African, 0.1),
                    (Race.European, 0.3),
                    (Race.Middle_Eastern, 0.1),
                    (Race.South_Asian, 0.2),
                    (Race.Hispanic_or_Latin_American, 0.1),
                    (Race.Other, 0.2),
                ],
                ScenarioAttribute.YEAR_LEVEL.value: [
                    (0, 0.2),
                    (1, 0.2),
                    (2, 0.2),
                    (3, 0.2),
                    (4, 0.2),
                ],
            }
        )

        students = MockStudentProvider(student_provider_settings).get()

        students_weird = [student.to_weird_survey_thingy() for student in students]
        headers = students_weird[0].keys()
        with open(f'data/weird{idx}.csv', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=headers, delimiter=';')
            writer.writeheader()
            writer.writerows(students_weird)


def load_data():
    scenario = ConcentrateTimeAvailabilityDiversifyGenderMin2Female(Gender.FEMALE.value)
    metric = PrioritySatisfaction(
        goals_to_priorities(scenario.goals),
        False,
    )

    their_scores = []
    our_scores = []

    NUM_DATAPOINT = 1000

    for idx in range(NUM_DATAPOINT):
        df = pd.read_csv(f'their_data/out-private-{idx + 1}.csv')
        teams = {}
        for _, row in df.iterrows():
            new_student = Student(
                _id=row['sid'],
                name=row['first_name'] + ' ' + row['last_name'],
                attributes={
                    ScenarioAttribute.YEAR_LEVEL.value: [int(row['year'])],
                    ScenarioAttribute.RACE.value: [fromAlRaceToRace(int(row['race'])).value],
                    ScenarioAttribute.GENDER.value: [fromAlGenderToGender(int(row['gender'])).value],
                    ScenarioAttribute.TIMESLOT_AVAILABILITY.value: list(
                        map(int, row['disc_times_options'].strip("[']").split(','))),
                }
            )
            if row['group_num'] not in teams:
                teams[row['group_num']] = Team(_id=row['group_num'])
            teams[row['group_num']].add_student(new_student)

        weird_algo_teamset = TeamSet(teams=list(teams.values()))

        all_students = [student for team in weird_algo_teamset.teams for student in team.students]
        random.shuffle(all_students)

        priority_algorithm = PriorityAlgorithm(
            algorithm_options=PriorityAlgorithmOptions(
                priorities=goals_to_priorities(scenario.goals),
                attributes_to_concentrate=[ScenarioAttribute.TIMESLOT_AVAILABILITY.value],
                attributes_to_diversify=[ScenarioAttribute.GENDER.value],
                max_project_preferences=0,
            ),
            algorithm_config=PriorityAlgorithmConfig(
                MAX_KEEP=100,
                MAX_SPREAD=100,
                MAX_ITERATE=1500,
                MAX_TIME=10000,
            ),
            team_generation_options=TeamGenerationOptions(
                max_team_size=6,
                min_team_size=3,
                total_teams=weird_algo_teamset.num_teams,
                initial_teams=[],
            )
        )

        our_teamset = priority_algorithm.generate(all_students)

        ok_dict = {}
        for team in our_teamset.teams:
            for student in team.students:
                ok_dict['sid'] = student.id
                ok_dict['group_num'] = team.id
                ok_dict['first_name'] = student.name.split(' ')[0]
                ok_dict['last_name'] = student.name.split(' ')[1]
                ok_dict['year'] = fromYearLevelToAlYearLevel(
                    student.attributes[ScenarioAttribute.YEAR_LEVEL.value][0]).value
                ok_dict['gender'] = fromGenderToAlGender(
                    Gender(student.attributes[ScenarioAttribute.GENDER.value][0])).value
                ok_dict['race'] = fromRaceToAlRace(Race(student.attributes[ScenarioAttribute.RACE.value][0])).value
                ok_dict['disc_times_options'] = fromNumbersToTimeSlots(
                    student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value])

        df = pd.DataFrame.from_dict(ok_dict)
        df.to_csv(f'our_data/our{idx + 1}.csv')

        their_score = metric.calculate(weird_algo_teamset)
        their_scores.append(their_score)
        our_score = metric.calculate(our_teamset)
        our_scores.append(our_score)

        print(f'Our score: {our_score}, their score: {their_score}')

    # plot duo line graphs, y is score, x is idx
    plt.plot(range(NUM_DATAPOINT), their_scores, label='their')
    plt.plot(range(NUM_DATAPOINT), our_scores, label='our')
    plt.legend()
    # Save the image
    plt.savefig('graphs/our_data.png')
    plt.show()


def run_and_save(idx):
    # df = pd.read_csv(f'/home/phngtuki/algorithms/benchmarking/runs/their_data/out-private-{idx + 1}.csv')
    df = pd.read_csv(f'their_data/out-private-{idx + 1}.csv')
    student_provider = CoolStudentProvider(idx)
    teams = {}
    for _, row in df.iterrows():
        new_student = Student(
            _id=row['sid'],
            name=row['first_name'] + ' ' + row['last_name'],
            attributes={
                ScenarioAttribute.YEAR_LEVEL.value: [int(row['year'])],
                ScenarioAttribute.RACE.value: [fromAlRaceToRace(int(row['race'])).value],
                ScenarioAttribute.GENDER.value: [fromAlGenderToGender(int(row['gender'])).value],
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value: list(
                    map(int, row['disc_times_options'].strip("[']").split(','))),
            }
        )
        if row['group_num'] not in teams:
            teams[row['group_num']] = Team(_id=row['group_num'])
        teams[row['group_num']].add_student(new_student)

    weird_algo_teamset = TeamSet(teams=list(teams.values()))

    sim_result = SimulationSet(
        settings=SimulationSettings(
            scenario=ConcentrateTimeAvailabilityDiversifyGenderMin2Female(Gender.FEMALE.value),
            student_provider=student_provider,
            num_teams=weird_algo_teamset.num_teams,
            cache_key=f'weirdAlgo/our_data-{idx + 1}',
        ),
        algorithm_set={
            AlgorithmType.PRIORITY: [
                PriorityAlgorithmConfig(
                    MAX_KEEP=50,
                    MAX_SPREAD=50,
                    MAX_ITERATE=1000,
                    MAX_TIME=10000,
                )
            ],
        }
    ).run(num_runs=30)

    # ok_dict = {
    #     'sid': [],
    #     'group_num': [],
    #     'first_name': [],
    #     'last_name': [],
    #     'year': [],
    #     'gender': [],
    #     'race': [],
    #     'disc_times_options': [],
    # }
    # for team in our_teamset.teams:
    #     for student in team.students:
    #         ok_dict['sid'].append(student.id)
    #         ok_dict['group_num'].append(team.id)
    #         ok_dict['first_name'].append(student.name.split(' ')[0])
    #         ok_dict['last_name'].append(student.name.split(' ')[1])
    #         ok_dict['year'].append(fromYearLevelToAlYearLevel(student.attributes[ScenarioAttribute.YEAR_LEVEL.value][0]).value)
    #         ok_dict['gender'].append(fromGenderToAlGender(Gender(student.attributes[ScenarioAttribute.GENDER.value][0])).value)
    #         ok_dict['race'].append(fromRaceToAlRace(Race(student.attributes[ScenarioAttribute.RACE.value][0])).value)
    #         ok_dict['disc_times_options'].append(fromNumbersToTimeSlots(student.attributes[ScenarioAttribute.TIMESLOT_AVAILABILITY.value]))
    #
    # df = pd.DataFrame.from_dict(ok_dict)
    # df.to_csv(f'/home/phngtuki/algorithms/benchmarking/runs/our_correct_data/our{idx + 1}.csv')


class CoolStudentProvider(StudentProvider):
    def get(self, seed: int = None) -> List[Student]:
        return self.students

    def __init__(self, idx):
        self.idx = idx
        df = pd.read_csv(f'data/weird{idx}.csv', delimiter=';')
        self.students = [Student(
            _id=row['SID'],
            name=row['First name'] + ' ' + row['Last name'],
            attributes={
                ScenarioAttribute.YEAR_LEVEL.value: [fromAlYearLevelToYearLevel(row['What year are you'])],
                ScenarioAttribute.RACE.value: [
                    fromAlRaceToRace(row['Which of these options best describes your race?']).value],
                ScenarioAttribute.GENDER.value: [fromAlGenderToGender(row['How do you self-identify?']).value],
                ScenarioAttribute.TIMESLOT_AVAILABILITY.value: fromTimeslotsToNumbers(
                    row['discussion section times'].strip("[']").split(','))
            }
        ) for _, row in df.iterrows()]

    @property
    def num_students(self):
        return len(self.students)

    @property
    def max_project_preferences_per_student(self) -> int:
        return 0


import threading


def run_and_save_multithreads():
    def worker(start, end):
        for idx in range(start, end):
            run_and_save(idx)

    num_threads = 1000

    step = 1000 // num_threads
    ranges = [(i * step, (i + 1) * step) for i in range(num_threads)]

    threads = []
    for start, end in ranges:
        thread = threading.Thread(target=worker, args=(start, end))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # load_data()
    # generate_data()
    run_and_save_multithreads()
