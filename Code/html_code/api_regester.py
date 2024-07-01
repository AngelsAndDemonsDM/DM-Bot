import os

from flask import Blueprint

static_folder = os.path.join(os.path.dirname(__file__), '..', 'web', 'static')
template_folder = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates')

api_bp = Blueprint('api', __name__, static_folder=static_folder, template_folder=template_folder)
