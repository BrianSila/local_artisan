from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv["error"] = self.message
        return rv


class NotFoundError(APIError):
    status_code = 404


class ForbiddenError(APIError):
    status_code = 403


class UnauthorizedError(APIError):
    status_code = 401


class ConflictError(APIError):
    status_code = 409


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(err):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        return jsonify({"error": "Database integrity error", "details": str(err.orig)}), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({"error": "Internal server error"}), 500