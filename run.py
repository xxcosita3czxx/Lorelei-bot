import logging
import os
import sys
import threading
import time

import click
import psutil

import config
from utils.configmanager import lang

conflang = f"{config.language}"

logging.basicConfig(
    level=config.loglevel,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger("runner")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def update():
    if not config.autoupdate:
        return

    try:
        os.system("git stash push -- config.py")  # noqa: S605
        changed_files = os.popen("git diff --name-only origin/main").read().splitlines()  # noqa: E501, S605
        os.system("git pull")  # noqa: S605
        os.system("git stash pop")  # noqa: S605

        if changed_files:
            logger.info("Changed files: %s", changed_files)

        lang_updated = any("lang/" in f or "language/" in f for f in changed_files)
        command_updated = any("commands/" in f for f in changed_files)
        other_updated = any(
            not (f.startswith("commands/") or f.startswith("lang/") or f.startswith("language/"))  # noqa: E501
            for f in changed_files
        )

        if other_updated:
            logger.info("Other files updated. Restarting bot immediately...")
            os.system("python3 devtools/helper_cli.py kill")  # noqa: S605, S607
            return  # Stop here, no need to do more

        if lang_updated:
            logger.info("Language files updated. Reloading language...")
            os.system("python3 devtools/helper_cli.py reload_lang")  # noqa: S605, S607

        if command_updated:
            logger.info("Command files updated. Reloading commands...")
            os.system("python3 devtools/helper_cli.py extensions reload_all")  # noqa: S605, S607

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
            if 'python' in process.info['name'] and 'main.py' in ' '.join(process.info['cmdline']):  # noqa: E501
                main_pid = process.info['pid']

                logger.debug(
                    lang.get(conflang,"RunnerLogs","debug_on_pid_log") + str(main_pid),  # noqa: E501
                )
        if not main_pid:
            logger.info(lang.get(conflang,"RunnerLogs","info_not_running"))
            os.system("python3 main.py")  # noqa: S605, S607
        time.sleep(config.Is_Alive_time)
def update_cosita_tk():
    while True:
        try:
            os.system("python3 utils/cosita_toolkit.py")  # noqa: S605, S607
        except Exception:
            logger.error(lang.get(conflang,"RunnerLogs","err_costk_update_fail"))
        time.sleep(config.costk_update)

def ptero_mode():
        while True:
            for line in sys.stdin:
                os.system("python3 devtools/helper_cli.py " + line)  # noqa: S605

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
