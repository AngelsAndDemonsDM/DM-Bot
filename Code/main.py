import argparse
import asyncio
import logging
import os
import platform
import signal
import subprocess
import sys
import webbrowser

from auto_updater import needs_update
from colorlog import ColoredFormatter
from db_work import SettingsManager
from flask import Flask
from html_code import api_bp, html_error_bp
from html_code.api import handle_show_popup, shutdown_start
from html_code.socketio_regester import socketio

app = Flask(__name__)

socketio.init_app(app)

# Blueprint
app.register_blueprint(html_error_bp, url_prefix='/error')
app.register_blueprint(api_bp, url_prefix='/api')

# Argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description='DM-Bot')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    return parser.parse_args()

# Async helper function
async def async_main_bg_task():
    pass

# Background task function
def main_bg_task():
    asyncio.run(async_main_bg_task())

# Function to run a file in a new console
def run_file_in_new_console(file_path):
    absolute_path = os.path.abspath(file_path)
    system = platform.system()
    
    if system == "Windows":
        subprocess.Popen(["start", "cmd", "/c", f"python {absolute_path}"], shell=True)
    
    elif system == "Darwin":
        subprocess.Popen(["open", "-a", "Terminal", absolute_path])
    
    else:
        subprocess.Popen(["x-terminal-emulator", "-e", f"python {absolute_path}"])

# Start program
if __name__ == "__main__":
    args = parse_arguments()
    debug = args.debug
    
    if asyncio.run(SettingsManager().get_setting("app.auto_update")):
        if needs_update():
            logging.info("Updating application...")
            run_file_in_new_console(os.path.join("Code", "auto_updater", "update.py"))
            sys.exit(0)
    
    logger = logging.getLogger()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "[%(asctime)s] [%(log_color)s%(levelname)s%(reset)s] - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        },
        secondary_log_colors={},
        style='%'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    def signal_handler(signal, frame):
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    if not debug:
        webbrowser.open("http://127.0.0.1:5000")
    
    socketio.start_background_task(main_bg_task)
    
    socketio.run(app, debug=debug, allow_unsafe_werkzeug=True)
