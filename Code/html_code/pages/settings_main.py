import asyncio

from auto_updater import needs_update
from db_work import SettingsManager
from flask import render_template
from html_code.socketio_regester import socketio


def render_settings_main_page():
    return render_template('settings/settings_main.html')

# Работа с автоматическим обновлением
@socketio.on('settingSetUpAutoUpdate')
def get_auto_update(data) -> None:
    flag: bool
    
    try:
        asyncio.run(SettingsManager().set_setting("app.auto_update", data))
        flag = True
    
    except Exception:
        flag = False
    
    socketio.emit("settingAutoUpdateStatusPopup", flag)
    handle_check_auto_update_status()

@socketio.on('settingCheckAutoUpdate')
def handle_check_auto_update_status():
    auto_update = asyncio.run(SettingsManager().get_setting("app.auto_update"))
    socketio.emit('settingAutoUpdateStatusUpdate', auto_update)

# Получение информации о версиях
@socketio.on('getVersionInfo')
def handle_get_version_info():
    _, current_version, latest_version = needs_update()
    
    version_info = {
        "currentVersion": current_version,
        "latestVersion": latest_version
    }
    
    socketio.emit('versionInfo', version_info)
