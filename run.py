import os
import time
import threading
import utils.cosita_toolkit as ctkit
import logging
import coloredlogs
import socket
coloredlogs.install(level='INFO', fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


logger = logging.getLogger(__name__)


def update_run_monitor():
    while True:
        try:
            # Check network connectivity
            host = "www.google.com"  # Change to a reliable host
            port = 80
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            logger.info("Network connection established.")

            # Update and run logic
            update_succes = ctkit.update_script_from_github("xxcosita3czxx", "Lorelei-bot", "main.py", "./main.py")
            ctkit.update_script_from_github("xxcosita3czxx", "Cosita-ToolKit", "cosita_toolkit.py", "./utils/cosita_toolkit.py")
            ctkit.update_script_from_github("xxcosita3czxx", "Lorelei-bot", "run.py", "./run.py")

            if update_succes == 1:
                os.system("pkill -f main.py")
            else:
                logger.info(f"no update :D (CODE: {update_succes})")

            # Main script monitoring
            main_pid = os.popen("pgrep -f main.py").read()
            if not main_pid:
                logger.info("main.py is not running. Restarting...")
                os.system("python3 main.py")

        except (socket.error, Exception) as e:
            logger.error(f"An error occurred: {e}")
            logger.info("Waiting 60 seconds before retrying...")
            time.sleep(60)

        # Sleep between iterations
        time.sleep(10)

if __name__ == "__main__":
    update_thread = threading.Thread(target=update_run_monitor)
    update_thread.start()