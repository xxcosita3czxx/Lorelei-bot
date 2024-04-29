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
            update_success = ctkit.github_api.pull_repo(".")
        except Exception as e:
            logger.warning(f"git pull failed, pulling with http api: {e}")
            update_success = ctkit.github_api.update_repo_files_http("xxcosita3czxx", "lorelei-bot", "main",["run.py","main.py"])
        logger.info(update_success)
        if update_succes == 2:
            os.system("pkill -f main.py")
            logger.info("success, killing main.py...")
        elif update_success == 1:
            logger.info(f"no update :D (CODE: {update_succes})")
        else:
            logger.error("UPDATE FAILED")
    except Exception as e:
        logger.error(f"Error while trying to update, Install git, or if issue persist after autoscheduled update, create issue page on github -->> {e}")
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
def update_cosita_tk():
    while True:
        try:
            os.system(f"python3 utils/cosita_toolkit.py")
        except Exception as e:
            logger.error("CosTK update FAILED")
        time.sleep(360)
if __name__ == "__main__":
    update_thread = threading.Thread(target=update_loop)
    monitor_thread = threading.Thread(target=main_script_monitor)
    update_costk_thread = threading.Thread(target=update_cosita_tk)
    
    monitor_thread.start()
    update_thread.start()
    update_costk_thread.start()
