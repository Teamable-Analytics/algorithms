from django.http import HttpResponse

from utils.api_auth import is_api_key_valid
from rest_framework.response import Response


class APIKeyAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        request_headers = dict(request.headers)
        api_key = request_headers.get("X-Api-Key")
        if not api_key:
            return HttpResponse("No API key provided", status=400)
        if not is_api_key_valid(api_key):
            return HttpResponse("Invalid API key provided", status=401)

        return response
