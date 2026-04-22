from functools import wraps
from flask import (current_app, jsonify, request)
from jsonschema import validate, ValidationError
from werkzeug.exceptions import BadRequest

def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        ctype = request.headers.get("Content-Type", "")
        method_ = request.headers.get("X-HTTP-Method-Override", request.method)

        if method_.lower() == request.method.lower() and "json" in ctype.lower():
            try:
                request.json
            except BadRequest:
                return jsonify({"error": "This is an invalid json"}), 400

        return f(*args, **kw)

    return wrapper

def validate_schema(schema_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                # 조금 전 정의하 json 파일대로 json의 body 메세지가 보내졌는지 확인한다
                validate(request.json, current_app.config[schema_name])
            except ValidationError as e:
                return jsonify({'error': e.message}), 400
            return f(*args, **kw)
        return wrapper
    return decorator