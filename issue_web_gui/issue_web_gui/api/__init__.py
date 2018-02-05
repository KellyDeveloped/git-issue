from flask import Blueprint
from flask_restplus import Api

bp = Blueprint('api', __name__)
api = Api(bp)

@bp.after_request
def add_cors(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response