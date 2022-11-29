from algorithm_sandbox.student_data import fake_students

"""
Scenario 1

A class of 20 students should form 4 teams of 5 student.
Everything is random and uniformly distributed.
The aim is to have as much diversity as possible.

"""


def get_s1_student():
    return fake_students(
        number_of_students=20,
        number_of_friends=10,
        number_of_enemies=2,
        age_range=[18, 25],
        age_distribution='uniform',
        gender_options=['MALE', 'FEMALE'],
    )


"""
Scenario 2

A class of 20 students should form 4 teams of 5 student.
there are 7 girls in the class and the aim is to not have isolated girls. 
"""


def get_s2_student():
    return fake_students(
        number_of_students=20,
        number_of_friends=10,
        number_of_enemies=2,
        age_range=[18, 25],
        age_distribution='uniform',
        gender_options={
            'MALE': 13,
            'FEMALE': 7,
        }
    )


"""
Scenario 3

A class of 150 students should form 50 teams of 3 students.
In this class there are clusters of sizes 3-5 which want to be in the same team.
The goal is to satisfy as much of these clusters as possible.
"""


"""
Scenario 4

A class of 500 students should work on 100 projects.
Each project requires 3 skills (out of 10 possible skills). 
The skills of students are uniformly distributed.
The goal is to satisfy all the project requirements.
"""


"""
Scenario 5

A class of 500 students should form 20 labs of 25 students.
The requirement if the timezone availability, each student has random availability
among 5 possible values.
The goal is to be able to put everyone in a lab.
"""