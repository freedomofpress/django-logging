import time

from django.db import connections
from . import log
from . import settings
from .log_object import LogObject, ErrorLogObject, SqlLogObject


class DjangoLoggingMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        start_time = time.perf_counter_ns()
        response = self.get_response(request)
        duration = (time.perf_counter_ns() - start_time) // 1_000_000

        return self.process_response(request, response, duration)

    def process_exception(self, request, exception):
        error = ErrorLogObject(request, exception)
        log.error(error)

    def process_response(self, request, response, duration):
        for connection in connections.all():
            self.log_connection_queries(connection)

        if request.path_info.startswith(tuple(settings.IGNORED_PATHS)):
            return response

        if response.status_code == 500:
            return response
        elif 400 <= response.status_code < 500:
            log.warning(LogObject(request, response, duration))
        else:
            log.info(LogObject(request, response, duration))
        return response

    def log_connection_queries(self, connection):
        for query in connection.queries:
            log.debug(SqlLogObject(query, connection.alias))
