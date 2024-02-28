from rest_framework import viewsets
from rest_framework.decorators import action

from api.api.utils.response_with_metadata import ResponseWithMetadata
from api.models.student import StudentSerializer
from benchmarking.data.simulated_data.mock_student_provider import (
    MockStudentProviderSettings,
    MockStudentProvider,
)


class SimulatePeopleViewSet(viewsets.ViewSet):
    @action(url_path="people", detail=False, methods=["POST"])
    def generate_class(self, request):
        try:
            request_data = dict(request.data)

            # Parse the attribute ranges
            attribute_ranges_raw = request_data.get("attribute_ranges", {})
            attribute_ranges = {}
            for attribute_id, attribute_values in attribute_ranges_raw.items():
                if (
                    type(attribute_values) is not dict
                    and type(attribute_values) is not list
                ):
                    raise ValueError(
                        f"Invalid value type for attribute_range[{attribute_id}]"
                    )
                if type(attribute_values) is dict:
                    attribute_ranges[int(attribute_id)] = [
                        (int(attr_value), float(attr_probability))
                        for attr_value, attr_probability in attribute_values.items()
                    ]
                if type(attribute_values) is list:
                    attribute_ranges[int(attribute_id)] = attribute_values

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
                error=f"Missing key {str(e)}", data_label="students", status=400
            )
        except ValueError as e:
            return ResponseWithMetadata(error=str(e), data_label="students", status=400)
        except Exception as e:
            return ResponseWithMetadata(error=str(e), data_label="students", status=500)
