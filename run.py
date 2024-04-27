import os
import time
import threading
import utils.cosita_toolkit as ctkit
import logging
import coloredlogs
import psutil

coloredlogs.install(level='DEBUG', fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
# Get the full path to the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def update_and_run():
    try:
        try:
            update_succes = ctkit.github_api.pull_repo(".")
        except:
            logger.warning("git pull failed, pulling with http api")
            update_success = ctkit.github_api.update_repo_files_http("xxcosita3czxx", "lorelei-bot", "main")
        if update_succes == 2:
            os.system("pkill -f main.py")
            logger.info("success, killing main.py...")
        else:
            logger.info(f"no update :D (CODE: {update_succes})")
    except Exception as e:
        return f"Error while trying to update, Install git, or if issue persist after autoscheduled update, create issue page on github -->> {e}"
def update_loop():
    while True:
        update_and_run()
        time.sleep(120)
def main_script_monitor():
    while True:
        main_pid = None
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'python3' in process.info['name'] and 'main.py' in ' '.join(process.info['cmdline']):
                main_pid = process.info['pid']
                logger.debug("main.py is running at PID: " + str(main_pid))
                break
        if not main_pid:
            logger.info("main.py is not running. Restarting...")
            os.system("python3 main.py")
        time.sleep(30)

if __name__ == "__main__":
    update_thread = threading.Thread(target=update_loop)
    monitor_thread = threading.Thread(target=main_script_monitor)

    monitor_thread.start()
    update_thread.start()
