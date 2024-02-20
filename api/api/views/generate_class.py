from rest_framework import viewsets
from rest_framework.decorators import action

from api.api.utils.response_with_metadata import ResponseWithMetadata
from api.models.enums import AttributeValueEnum
from api.models.student import StudentSerializer
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)


class GenerateClassViewSet(viewsets.ViewSet):
    @action(url_path="class", detail=False, methods=["POST"])
    def generate_class(self, request):
        """
        Steps to do this:
        0. Permissions/access/api keys/etc
        1. Read JSOM
            1.1 Parse to dict
            1.2 Throw error if invalid JSON
        2. Encode data from JSON to the correct Dataclasses (hopefully can import?)
            2.1 Validate dataclasses (so logical validation of values)
        3. Generate class
        4. Serialize class to JSON
        5. Return JSON to a happy user :) 🚀!
        """
        try:
            request_data = dict(request.data)

            # Parse the attribute ranges
            attribute_ranges_raw = request_data.get("attribute_ranges", {})
            attribute_ranges = {}
            for key, value_dict in attribute_ranges_raw.items():
                if type(value_dict) is not dict and type(value_dict) is not list:
                    raise ValueError(f"Invalid value type for attribute_range[{key}]")
                if type(value_dict) is dict:
                    attribute_ranges[int(key)] = [
                        (int(k), float(v)) for k, v in value_dict.items()
                    ]
                if type(value_dict) is list:
                    attribute_ranges[int(key)] = value_dict

            project_preference_options = list(
                map(int, request_data.get("project_preference_options", []))
            )

            student_provider_settings = MockStudentProviderSettings(
                number_of_students=int(request_data["class_size"]),
                attribute_ranges=attribute_ranges,
                project_preference_options=project_preference_options,
                num_project_preferences_per_student=int(
                    request_data.get("num_project_preferences_per_student", 0)
                ),
                number_of_friends=int(request_data.get("number_of_friends", 0)),
                number_of_enemies=int(request_data.get("number_of_enemies", 0)),
            )
            student_provider_settings.validate()

            students = MockStudentProvider(student_provider_settings).get()
            json_student = [
                StudentSerializer().default(student) for student in students
            ]
            return ResponseWithMetadata(
                data=json_student, data_label="students", status=200
            )
        except KeyError as e:
            return ResponseWithMetadata(
                error=f"Missing key {str(e)}", data_label="students", status=500
            )
        except Exception as e:
            return ResponseWithMetadata(error=str(e), data_label="students", status=500)
