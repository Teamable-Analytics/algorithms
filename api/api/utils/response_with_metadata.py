import time

from rest_framework.response import Response

from api import api


class ResponseWithMetadata(Response):
    def __init__(
        self,
        data_label,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        timestamp=None,
        error=None,
    ):
        super().__init__(data, status, template_name, headers, exception, content_type)

        if not data and not error:
            raise ValueError("data must be provided")
        if not data_label:
            raise ValueError("data_label must be provided")

        self.data = {
            data_label: self.data,
            "metadata": {
                "version": api.VERSION,
                "timestamp": timestamp if timestamp else time.time(),
            },
            "error": error,
        }
