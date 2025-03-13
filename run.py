import logging
import os
import sys
import threading
import time

import click
import coloredlogs
import psutil

import config
from utils.configmanager import lang

conflang = f"{config.language}"

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger("runner")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def update():
    if config.autoupdate:
        try:
            os.system("git stash push -- config.py") # noqa: S605
            os.system("git pull") # noqa: S605
            os.system("git stash pop") # noqa: S605
        except Exception as e:
            logger.warning("UPDATER FAILED")
            logger.warning(e)
def update_loop():
    while True:
        update()
        time.sleep(config.bot_update)
def Is_Alive():
    while True:
        main_pid = None
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'python3' in process.info['name'] and 'main.py' in ' '.join(process.info['cmdline']):  # noqa: E501
                main_pid = process.info['pid']

                logger.debug(
                    lang.get(conflang,"RunnerLogs","debug_on_pid_log") + str(main_pid),  # noqa: E501
                )
        if not main_pid:
            logger.info(lang.get(conflang,"RunnerLogs","info_not_running"))
            os.system("python main.py")  # noqa: S605, S607
        time.sleep(config.Is_Alive_time)
def update_cosita_tk():
    while True:
        try:
            os.system("python utils/cosita_toolkit.py")  # noqa: S605, S607
        except Exception:
            logger.error(lang.get(conflang,"RunnerLogs","err_costk_update_fail"))
        time.sleep(config.costk_update)

def ptero_mode():
        while True:
            for line in sys.stdin:
                os.system("python3 helper.py " + line)  # noqa: S605

@click.command()
@click.option("--update",is_flag=True, help="Updates the bot and exits")
def main(update):
    if update:
        update()
        os.system("python3 utils/cosita_toolkit.py") # noqa: S605
        sys.exit()

    if not os.path.exists(".secret.key") or open(".secret.key").read().strip() == "":  # noqa: E501, SIM115
        logger.error("TOKEN NOT FOUND, PLEASE ADD TOKEN TO .secret.key")
        if not os.path.exists(".secret.key"):
            with open(".secret.key", "w") as f:
                f.write("")
        sys.exit()
    monitor_thread = threading.Thread(target=Is_Alive)
    update_thread = threading.Thread(target=update_loop)
    update_costk_thread = threading.Thread(target=update_cosita_tk)

    monitor_thread.start()
    update_thread.start()
    update_costk_thread.start()

    if os.getenv("P_SERVER_UUID") is not None:
        ptero_thread = threading.Thread(target=ptero_mode)
        ptero_thread.start()

if __name__ == "__main__":
    main()
