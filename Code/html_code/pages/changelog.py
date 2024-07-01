import os

import yaml
from flask import render_template, request, url_for


def render_changelog_main_page():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    changelog_path = os.path.join(base_dir, '..', '..', '..', 'changelog.yml')

    with open(changelog_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        changelog = data.get('changelog', [])

    # Параметры пагинации
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total = len(changelog)
    pages = (total // per_page) + (1 if total % per_page else 0)

    # Срез данных для текущей страницы
    start = (page - 1) * per_page
    end = start + per_page
    changelog_paginated = changelog[start:end]

    # Формируем данные для пагинации
    pagination = {
        'prev': url_for('main.changelog_page', page=page-1) if page > 1 else None,
        'next': url_for('main.changelog_page', page=page+1) if page < pages else None,
        'pages': [(p, url_for('main.changelog_page', page=p)) for p in range(1, pages+1)],
        'current_page': page
    }

    return render_template('changelog.html', changelog=changelog_paginated, pagination=pagination)
