from flask import Blueprint, jsonify, request
from . import calculation
api = Blueprint('api', __name__)

@api.get('/')
def index():
    return jsonify({'colum': 'value'}), 201

@api.post('/detect')
def detection():
    return calculation.detection(request)
