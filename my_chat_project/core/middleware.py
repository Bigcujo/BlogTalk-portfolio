class HTMXMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.htmx = 'HX-Request' in request.headers
        response = self.get_response(request)
        return response


# core/middleware.py

import logging

logger = logging.getLogger(__name__)

class SessionDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session = request.session
        try:
            session_data = session.items()
            logger.debug(f"Session data: {session_data}")
        except Exception as e:
            logger.error(f"Error accessing session data: {e}")

        response = self.get_response(request)
        return response

class LogSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_key = request.session.session_key
        session_data = request.session.items()
        print(f"Session Key: {session_key}")
        print(f"Session Data: {session_data}")
        response = self.get_response(request)
        return response
