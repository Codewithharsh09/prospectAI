from flask import jsonify


def success_response(data=None, message: str = "Success", status_code: int = 200):
    payload: dict = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message: str, error_code: str, status_code: int = 400):
    return jsonify({"success": False, "message": message, "error_code": error_code}), status_code
