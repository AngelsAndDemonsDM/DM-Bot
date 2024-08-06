import argparse
import asyncio
import logging
import os
import platform
import signal
import subprocess
import sys
from logging.config import dictConfig

from api import *
from quart import Quart
from quart.logging import default_handler
from systems.auto_updater import AutoUpdater
from systems.db_systems import load_config
from systems.entity_system import EntityFactory
from systems.events_system import EventManager

http_server = Quart(__name__)
http_server.logger.removeHandler(default_handler)
logging.getLogger("websockets").addHandler(logging.NullHandler())
logging.getLogger("websockets").propagate = False

# Blueprint
http_server.register_blueprint(admin_bp, url_prefix='/admin')
http_server.register_blueprint(auth_bp, url_prefix='/auth')
http_server.register_blueprint(server_bp, url_prefix='/server')

# Argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description='DM-Bot')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    return parser.parse_args()

# Function to run a file in a new console
def run_file_in_new_console(file_path) -> None:
    absolute_path = os.path.abspath(file_path)
    system = platform.system()
    
    if system == "Windows":
        subprocess.Popen(["start", "cmd", "/c", f"python {absolute_path}"], shell=True)
    
    elif system == "Darwin":
        subprocess.Popen(["open", "-a", "Terminal", absolute_path])
    
    else:
        subprocess.Popen(["x-terminal-emulator", "-e", f"python {absolute_path}"])

def register_all() -> None:
    logging.info("EntityFactory starting work")
    ent_factory = EntityFactory()
    logging.info("EntityFactory finished work")
    
    logging.info("EventManager starting work")
    ev_manager = EventManager()
    logging.info("EventManager finished work")

async def main() -> None:
    host, port, socket_port, auto_update = load_config()

    if auto_update:
        updater = AutoUpdater()
        if updater.is_needs_update():
            run_file_in_new_console(os.path.join("Code", "auto_updater", "auto_updater.py"))
            sys.exit(0)
        else:
            del updater

    # Запуск WebSocket сервера
    socket_task = asyncio.create_task(start_websocket_server(host=host, port=int(socket_port)))

    # Запуск HTTP сервера
    http_task = asyncio.create_task(http_server.run_task(host=host, port=int(port)))

    async def shutdown():
        await http_server.shutdown()
        socket_task.cancel()
        http_task.cancel()
        await asyncio.gather(socket_task, http_task, return_exceptions=True)

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    await asyncio.gather(socket_task, http_task)

if __name__ == "__main__":
    args = parse_arguments()
    debug = args.debug

    # Базовая конфигурация логгера
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s]-[%(levelname)s] \"%(name)s\": %(message)s',
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {
            'level': logging.DEBUG if debug else logging.INFO,
            'handlers': ['default'],
        },
    })
    
    register_all()
    
    try:
        asyncio.run(main())
    
    except KeyboardInterrupt:
        logging.info("Server shutdown initiated by user.")
