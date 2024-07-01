import os

from flask import Blueprint, render_template

static_folder = os.path.join(os.path.dirname(__file__), '..', 'web', 'static')
template_folder = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates')

html_error_bp = Blueprint('errors', __name__, static_folder=static_folder, template_folder=template_folder)

@html_error_bp.app_errorhandler(401)
def unauthorized_error(error):
    return render_template('error_pages/401.html'), 401

@html_error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('error_pages/404.html'), 404

@html_error_bp.app_errorhandler(500)
def internal_error(error):
    return render_template('error_pages/500.html'), 500
