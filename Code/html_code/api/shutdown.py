import asyncio
import logging
import os
import signal

from html_code.api_regester import api_bp


@api_bp.route('/shutdown', methods=['GET'])
def shutdown_start():
    logging.info("Start shutdown systems")
    asyncio.run(shutdown_systems())
    
    logging.info("Exit program")
    shutdown_server()
    return

def shutdown_server():
    # Отправка сигнала SIGINT самому себе. Откровенно говоря выглядит как хуйня
    os.kill(os.getpid(), signal.SIGINT)

async def shutdown_systems():
    pass
