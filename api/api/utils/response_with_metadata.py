import json
import time

from rest_framework.response import Response


class ResponseWithMetadata(Response):
    def __init__(
        self,
        data_label=None,
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

        data_label = data_label if data_label else "data"
        data = data if type(data) is dict else json.loads(data)

        self.data = {
            data_label: data,
            "metadata": {
                "version": "v0.1.0",
                "timestamp": timestamp if timestamp else time.time(),
            },
            "error": error,
        }
