import time

from rest_framework import viewsets

from api.models import Student
from api.serializer import StudentSerializer
from api.utils.response_with_metadata import ResponseWithMetadata


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset, many=True)
        return ResponseWithMetadata(
            data_label="students",
            data=serializer.data,
            timestamp=time.time(),
            status=200,
            error=None
        )

    def retrieve(self, request, pk=None, *args, **kwargs):
        student_id = pk

        # Validation
        try:
            student = self.queryset.get(id=student_id)
        except Student.DoesNotExist:
            return ResponseWithMetadata(
                data_label="student",
                data=[],
                timestamp=time.time(),
                status=404,
                error=f"Student with id {student_id} not found."
            )

        # Serialize and return response
        serializer = self.serializer_class(student)
        return ResponseWithMetadata(
            data_label="student",
            data=serializer.data,
            timestamp=time.time(),
            status=200,
            error=None)
