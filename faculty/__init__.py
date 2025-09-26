from flask import Blueprint

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

from . import routes
