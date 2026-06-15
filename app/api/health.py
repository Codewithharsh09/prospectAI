import logging
import time
from datetime import datetime, timezone

from flask import Blueprint, jsonify, render_template
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


def _check_health() -> dict:
    t0 = time.monotonic()
    db_status = "healthy"
    db_error = None

    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        db_status = "unhealthy"
        db_error = str(exc).split("\n")[0]
        logger.error("Database health check failed", exc_info=True)

    response_ms = round((time.monotonic() - t0) * 1000, 1)
    overall = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall,
        "db_status": db_status,
        "db_error": db_error,
        "response_ms": response_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

 
@health_bp.route("/health", methods=["GET"])
def health_ui():
    h = _check_health()
    http_status = 200 if h["status"] == "healthy" else 503
    return render_template("health.html", **h), http_status


@health_bp.route("/health/json", methods=["GET"])
def health_json():
    h = _check_health()
    http_status = 200 if h["status"] == "healthy" else 503
    payload = {
        "success": h["status"] == "healthy",
        "service": "ProspectAI",
        "status": h["status"],
        "database": h["db_status"],
        "timestamp": h["timestamp"],
        "response_ms": h["response_ms"],
    }
    if h["db_error"]:
        payload["database_error"] = h["db_error"]
    return jsonify(payload), http_status
