# from enum import Enum
# from typing import Dict, List


# class Attributes(Enum):
#     SCORE = 0
#     TUTOR_PREFERENCE = 1
#     GROUP_SIZE = 2
    
#     # Each list should define the possible options for each column
#     global col_1_options
#     global col_2_options
#     global col_3_options
    
#     col_1_options = [
#                         'In-person before or after class', 
#                         'In-person nights or weekends', 
#                         'On zoom'
#                     ]
#     col_2_options = [
#                         'I am looking for a classmate to tutor me in BIOC 202', 
#                         'I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee', 
#                         'I am interested in being a peer tutor in BIOC 202'
#                     ]
#     col_3_options = [
#                         '1', 
#                         '2 to 3',
#                         '3+'
#                     ]

#     @staticmethod
#     def process_row(row: List[str]) -> Dict:
#         """
#         Process a row of the CSV file and map non-integer attributes to integers.

#         Args:
#             row (List[str]): A row from the CSV file containing student data.

#         Returns:
#             Dict: A dictionary with processed attributes for the student.
#         """

#         # Process timeslot (column 1)
#         if row[1] == col_1_options[0]:
#             timeslot = 1
#         elif row[1] == col_1_options[1]:
#             timeslot = 2
#         elif row[1] == col_1_options[2]:
#             timeslot = 3
#         else:
#             raise ValueError(f"Invalid timeslot: {row[1]}")

#         # Process tutor preference (column 2)
#         if row[2] == col_2_options[0]:
#             tutor_preference = 1
#         elif row[2] == col_2_options[1]:
#             tutor_preference = 2
#         elif row[2] == col_2_options[2]:
#             tutor_preference = 3
#         else:
#             raise ValueError(f"Invalid tutor preference: {row[2]}")

#         # Process group size (column 3)
#         if row[3] == col_3_options[0]:
#             group_size = 1
#         elif row[3] == col_3_options[1]:
#             group_size = 2
#         elif row[3] == col_3_options[2]:
#             group_size = 3
#         else:
#             group_size = -1

#         # Process score (column 4)
#         score = float(row[4])
#         score = 1 if score >= 0 else 0

#         return {
#             "timeslot": timeslot,
#             "tutor_preference": tutor_preference,
#             "group_size": group_size,
#             "score": score
#         }


from enum import Enum
from typing import Dict, List


class Attributes(Enum):
    SCORE = 0
    TUTOR_PREFERENCE = 1
    GROUP_SIZE = 2
    
    
    global col_1_options
    global col_2_options
    global col_3_options
    # Each list should define the possible options for each column containing a non-integer value
    col_1_options = [
        'In-person before or after class', 
        'In-person nights or weekends', 
        'On zoom'
    ]
    col_2_options = [
        'I am looking for a classmate to tutor me in BIOC 202', 
        'I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee', 
        'I am interested in being a peer tutor in BIOC 202'
    ]
    col_3_options = [
        '1', 
        '2 to 3',
        '3+'
    ]

    @staticmethod
    def process_row(row: List[str]) -> Dict:
        # Map text values to integers
        timeslot_map = {v: i + 1 for i, v in enumerate(col_1_options)}
        tutor_preference_map = {v: i + 1 for i, v in enumerate(col_2_options)}
        group_size_map = {v: i + 1 for i, v in enumerate(col_3_options)}

        timeslot = timeslot_map.get(row[1], None)
        tutor_preference = tutor_preference_map.get(row[2], None)
        group_size = group_size_map.get(row[3], None)
        score = 1 if float(row[4]) >= 0 else 0

        return {
            "timeslot": timeslot,
            "tutor_preference": tutor_preference,
            "group_size": group_size,
            "score": score
        }

    @staticmethod
    def revert_timeslot(timeslot: int) -> str:
        return Attributes.col_1_options[timeslot - 1]

    @staticmethod
    def revert_tutor_preference(tutor_preference: int) -> str:
        return Attributes.col_2_options[tutor_preference - 1]

    @staticmethod
    def revert_group_size(group_size: int) -> str:
        return Attributes.col_3_options[group_size - 1]
