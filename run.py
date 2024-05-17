import logging
import os
import threading
import time

import coloredlogs
import psutil

import config
import utils.cosita_toolkit as ctkit

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)
# Get the full path to the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# SAVE FOR LATER
#def update_and_run():
#    if config.autoupdate == True:
#        try:
#            try:
#                update_success = ctkit.github_api.pull_repo(".")
#            except Exception as e:
#                logger.warning(f"git pull failed, pulling with http api: {e}")
#                update_success = ctkit.github_api.update_repo_files_http("xxcosita3czxx", "lorelei-bot", "main",["run.py","main.py"])  # noqa: E501
#            logger.info(update_success)
#            if update_success == 2:
#                os.system("pkill -f main.py")
#                logger.info("success, killing main.py...")
#                main_pid = None
#                for process in psutil.process_iter(['pid', 'name', 'cmdline']):
#                    if 'python3' in process.info['name'] and 'main.py' in ' '.join(process.info['cmdline']):  # noqa: E501
#                        main_pid = process.info['pid']
#                        logger.debug("main.py is running at PID: " + str(main_pid))
#                if not main_pid:
#                    logger.info("main.py is not running. Restarting...")
#                    os.system("python3 main.py")
#            elif update_success == 1:
#                logger.info(f"no update :D (CODE: {update_succes})")
#            else:
#                logger.error("UPDATE FAILED")
#        except Exception as e:
#            logger.error(f"Error while trying to update, Install git, or if issue persist after autoscheduled update, create issue page on github -->> {e}")  # noqa: E501
#    else:
#        logger.warning("UPDATER IS OFF, YOU WILL HAVE TO UPDATE MANUALLY")


def update_and_run():
    if config.autoupdate:
        try:
            ctkit.update_script_from_github("xxcosita3czxx","lorelei-bot","main.py","main.py")
            ctkit.update_script_from_github("xxcosita3czxx","lorelei-bot","run.py","run.py")
        except Exception as e:
            logger.warning(e)
def update_loop():
    while True:
        update_and_run()
        time.sleep(config.bot_update)
def Is_Alive():
    while True:
        main_pid = None
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'python3' in process.info['name'] and 'main.py' in ' '.join(process.info['cmdline']):  # noqa: E501
                main_pid = process.info['pid']
                logger.debug("main.py is running at PID: " + str(main_pid))
        if not main_pid:
            logger.info("main.py is not running. Restarting...")
            os.system("python3 main.py")  # noqa: S605, S607
        time.sleep(config.Is_Alive_time)
def update_cosita_tk():
    while True:
        try:
            os.system("python3 utils/cosita_toolkit.py")  # noqa: S605, S607
        except Exception:
            logger.error("CosTK update FAILED")
        time.sleep(config.costk_update)
if __name__ == "__main__":
    update_thread = threading.Thread(target=update_loop)
    monitor_thread = threading.Thread(target=Is_Alive)
    update_costk_thread = threading.Thread(target=update_cosita_tk)

    monitor_thread.start()
    update_thread.start()
    update_costk_thread.start()
