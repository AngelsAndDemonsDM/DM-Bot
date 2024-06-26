from flask import Blueprint
from py_html.pages import (render_about_main_page, render_changelog_main_page,
                           render_index_main_page, render_players_main_page,
                           render_settings_main_page)

main_bp = Blueprint('main', __name__)

# Главное окно приложения
@main_bp.route('/')
def home_page():
    return render_index_main_page()

@main_bp.route('/player')
def players_page():
    return render_players_main_page()

# О говнюках =)
@main_bp.route('/about')
def about_page():
    return render_about_main_page()

@main_bp.route('/changelog', methods=['GET'])
def changelog_page():
    return render_changelog_main_page()

# # НАСТРОЙКИ
# Общие
@main_bp.route("/settings/main")
def settings_main_page():
    return render_settings_main_page()
