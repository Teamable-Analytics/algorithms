from typing import List, Dict, Union

import api
from api.api.models import APISource, APILog


class APILogger:
    @staticmethod
    def log(
        endpoint: str, data: Union[Dict, List], source: APISource = APISource.NORMAL
    ):
        APILog.objects.create(
            endpoint=endpoint,
            source=source,
            api_version=api.VERSION,
            data=data,
        )
