import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone

from flask import g, has_request_context, request
from pythonjsonlogger import jsonlogger


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, "request_id", "-")
            record.correlation_id = getattr(g, "correlation_id", "-")
            record.remote_addr = request.remote_addr
            record.http_method = request.method
            record.path = request.path
        else:
            record.request_id = "-"
            record.correlation_id = "-"
            record.remote_addr = "-"
            record.http_method = "-"
            record.path = "-"
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["service"] = "ProspectAI"
        log_record["logger"] = record.name


def setup_logging(app):
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_dir = app.config.get("LOG_DIR", "logs")

    os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    context_filter = RequestContextFilter()
    json_formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(message)s "
        "%(request_id)s %(correlation_id)s %(remote_addr)s %(http_method)s %(path)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(context_filter)

    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(context_filter)

    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(context_filter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
