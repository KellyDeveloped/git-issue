from flask import Blueprint
from flask_restplus import Api
from flask_cors import CORS

bp = Blueprint('api', __name__)
cors = CORS(bp)
api = Api(bp)