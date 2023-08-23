import os
import time
import threading
import utils.cosita_toolkit as ctkit
import logging
import coloredlogs
# Configure colorlog with colors
# handler = colorlog.StreamHandler()
# handler.setFormatter(colorlog.ColoredFormatter(
#     '%(log_color)s%(asctime)s %(levelname)s: %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     log_colors={
#         'DEBUG': 'cyan',
#         'INFO': 'green',
#         'WARNING': 'yellow',
#         'ERROR': 'red',
#         'CRITICAL': 'bold_red',
#     }
# ))

# # Create a logger
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)

coloredlogs.install(level='INFO', fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create a logger
logger = logging.getLogger(__name__)


def update_and_run():
    update_succes = ctkit.update_script_from_github("xxcosita3czxx", "Lorelei-bot", "main.py", "./main.py")
    ctkit.update_script_from_github("xxcosita3czxx", "Cosita-ToolKit", "cosita_toolkit.py", "./utils/cosita_toolkit.py")
    ctkit.update_script_from_github("xxcosita3czxx", "Lorelei-bot", "run.py", "./run.py")
    if update_succes == 1:
        os.system("pkill -f main.py")
        os.system("python3 main.py")
    else:
        logger.info(f"no update :D (CODE: {update_succes})")
def update_loop():
    while True:
        update_and_run()
        time.sleep(60)
def main_script_monitor():
    while True:
        main_pid = os.popen("pgrep -f main.py").read()
        if not main_pid:
            logging.INFO("main.py is not running. Restarting...")
            update_and_run()
        time.sleep(10)
if __name__ == "__main__":
    update_thread = threading.Thread(target=update_loop)
    update_thread.start()
    monitor_thread = threading.Thread(target=main_script_monitor)
    monitor_thread.start()
    os.system("python main.py")