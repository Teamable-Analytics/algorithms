import json
import os


def survey_filter(file_path, dropout_id):
    friend_enemy_attr_id = []
    student = []
    removal_required = []

    for survey in os.listdir(file_path):
        if survey.endswith('.txt'):
            os.rename(src=file_path, dst=file_path.replace('.txt', '.json'))

    for json_file in os.listdir(file_path):
        json_file_path = os.path.join(file_path, json_file)
        with open(json_file_path, "r") as f:
            survey_json = json.loads(f.read())

            for attr_id, serialize_attribute_info in survey_json["attribute_info"].items():
                if serialize_attribute_info["attr_type"] == "Include Friends/Exclude Enemies":
                    friend_enemy_attr_id.append(attr_id)

            for student_id, serialize_student_info in survey_json["student_info"].items():
                if serialize_student_info["role"] == "Student":
                    student.append(student_id)

            for student_id, serialize_student_responses in survey_json["student_responses"].items():
                if student_id in student and int(student_id) not in dropout_id:
                    for attr_id in friend_enemy_attr_id:
                        if serialize_student_responses[attr_id] is not None:
                            if int(student_id) in serialize_student_responses[attr_id]:
                                removal_required.append(student_id)

                else:
                    removal_required.append(student_id)

            return removal_required
