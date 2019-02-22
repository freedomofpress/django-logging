import datetime
import json
import gzip
import time
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from . import settings
from .log_object import LogObject, ErrorLogObject, SqlLogObject


def message_from_record(record):
    if isinstance(record.msg, dict):
        message = record.msg
    elif isinstance(record.msg, Exception):
        message = ErrorLogObject.format_exception(record.msg)
    else:
        try:
            message = record.msg.to_dict
        except AttributeError:
            message = record.msg
    return message


class AppFileHandler(RotatingFileHandler):
    def emit(self, record):
        if not isinstance(record.msg, LogObject)\
                and not isinstance(record.msg, ErrorLogObject)\
                and not isinstance(record.msg, dict)\
                and not isinstance(record.msg, Exception):
            return

        return super(AppFileHandler, self).emit(record)

    def format(self, record):
        created = int(record.created)
        message = message_from_record(record)
        return json.dumps({record.levelname: {created: message}}, sort_keys=True)

    def rotation_filename(self, default_name):
        return '{}-{}.gz'.format(default_name, time.strftime('%Y%m%d'))

    def rotate(self, source, dest):
        with open(source, 'rb+') as fh_in:
            with gzip.open(dest, 'wb') as fh_out:
                fh_out.writelines(fh_in)
            fh_in.seek(0)
            fh_in.truncate()


class DebugFileHandler(RotatingFileHandler):
    def emit(self, record):
        if not isinstance(record.msg, LogObject) \
                and not isinstance(record.msg, ErrorLogObject) \
                and not isinstance(record.msg, dict) \
                and not isinstance(record.msg, Exception)\
                and not isinstance(record.msg, SqlLogObject):
            return super(DebugFileHandler, self).emit(record)

    def format(self, record):
        created = int(record.created)
        message = message_from_record(record)
        return json.dumps({record.levelname: {created: message}}, sort_keys=True)

    def rotation_filename(self, default_name):
        return '{}-{}.gz'.format(default_name, time.strftime('%Y%m%d'))

    def rotate(self, source, dest):
        with open(source, 'rb+') as fh_in:
            with gzip.open(dest, 'wb') as fh_out:
                fh_out.writelines(fh_in)
            fh_in.seek(0)
            fh_in.truncate()


class ConsoleHandler(StreamHandler):
    def emit(self, record):
        return super(ConsoleHandler, self).emit(record)

    def format(self, record):
        if isinstance(record.msg, LogObject) or isinstance(record.msg, SqlLogObject):
            created = int(record.created)
            message = {record.levelname: {created: record.msg.to_dict}}

            return json.dumps(message,
                              sort_keys=True)
        elif isinstance(record.msg, ErrorLogObject):
            return str(record.msg)
        elif isinstance(record.msg, dict):
            created = int(record.created)
            message = {record.levelname: {created: record.msg}}
            return json.dumps(message, sort_keys=True)
        else:
            return super(ConsoleHandler, self).format(record)


class SQLFileHandler(RotatingFileHandler):
    def emit(self, record):
        if not isinstance(record.msg, SqlLogObject):
            return
        return super(SQLFileHandler, self).emit(record)

    def format(self, record):
        created = int(record.created)
        message = {record.levelname: {created: record.msg.to_dict}}
        return json.dumps(message, sort_keys=True)

    def rotation_filename(self, default_name):
        return '{}-{}.gz'.format(default_name, time.strftime('%Y%m%d'))

    def rotate(self, source, dest):
        with open(source, 'rb+') as fh_in:
            with gzip.open(dest, 'wb') as fh_out:
                fh_out.writelines(fh_in)
            fh_in.seek(0)
            fh_in.truncate()
