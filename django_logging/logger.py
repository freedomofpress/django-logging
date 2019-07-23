import logging
import logging.config
import os

import sys

from . import settings

LOG_LEVEL = settings.LOG_LEVEL.upper()
LOG_HANDLERS = dict()


def create_log_directory():
    """Create root logging directory if it doesn't already exist"""

    if not os.path.exists(settings.LOG_PATH):
        try:
            os.makedirs(settings.LOG_PATH)
        except Exception:
            raise Exception('Unable to configure logger. Can\'t create LOG_PATH: {}'.format(settings.LOG_PATH))


if settings.CONSOLE_LOG:
    LOG_HANDLERS['console'] = {
            'level': 'DEBUG',
            'class': 'django_logging.handlers.ConsoleHandler',
            'formatter': 'verbose',
            'stream': sys.stderr
        }

else:
    LOG_HANDLERS['default'] = {
            'level': 'INFO',
            'class': 'django_logging.handlers.AppFileHandler',
            'formatter': 'verbose',
            'maxBytes': settings.ROTATE_MB * 1024 * 1024,
            'backupCount': settings.ROTATE_COUNT,
            'filename': '{}/app.log'.format(settings.LOG_PATH)
        }
    create_log_directory()

if settings.DEBUG:
    LOG_HANDLERS['debug'] = {
            'level': 'DEBUG',
            'class': 'django_logging.handlers.DebugFileHandler',
            'formatter': 'verbose',
            'maxBytes': settings.ROTATE_MB * 1024 * 1024,
            'backupCount': settings.ROTATE_COUNT,
            'filename': '{}/debug.log'.format(settings.LOG_PATH)
        }
    create_log_directory()


if settings.SQL_LOG:
    LOG_HANDLERS['sql'] = {
            'level': 'DEBUG',
            'class': 'django_logging.handlers.SQLFileHandler',
            'formatter': 'sql',
            'maxBytes': settings.ROTATE_MB * 1024 * 1024,
            'backupCount': settings.ROTATE_COUNT,
            'filename': '{}/sql.log'.format(settings.LOG_PATH)
        }
    create_log_directory()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': settings.DISABLE_EXISTING_LOGGERS,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s - %(created)s], file:%(module)s.py, func:%(funcName)s, ln:%(lineno)s: %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        },
        'sql': {
            'format': '[%(levelname)s - %(created)s] %(duration)s %(sql)s %(params)s'
        },
    },
    'handlers': LOG_HANDLERS,
    'loggers': {
        'dl_logger': {
            'handlers': [h for h in LOG_HANDLERS],
            'level': LOG_LEVEL,
            'propagate': settings.PROPOGATE
        },
    }
}
logging.config.dictConfig(LOGGING)


def get_logger():
    logger = logging.getLogger('dl_logger')
    logger.setLevel(LOG_LEVEL)
    return logger
