import logging
import time
import uuid

from flask import g, request

logger = logging.getLogger(__name__)

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "no-referrer",
    # Allows inline styles/scripts for the health UI page; API responses carry no scripts anyway
    "Content-Security-Policy": "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'",
}


def register_middleware(app):
    @app.before_request
    def set_request_context():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.correlation_id = request.headers.get("X-Correlation-ID", g.request_id)
        g.start_time = time.monotonic()

    @app.after_request
    def finalize_response(response):
        duration_ms = round((time.monotonic() - g.start_time) * 1000, 2)

        response.headers["X-Request-ID"] = g.request_id
        response.headers["X-Correlation-ID"] = g.correlation_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        for header, value in _SECURITY_HEADERS.items():
            response.headers[header] = value

        logger.info(
            "Request completed",
            extra={
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
