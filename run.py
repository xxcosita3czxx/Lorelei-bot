import os
import time
import threading
import utils.cosita_toolkit as ctkit
def update_and_run():
    update_succes = ctkit.github_api.pull_updates("https://github.com/xxcosita3czxx/Lorelei-bot",".")
    if update_succes == 1:
        os.system("pkill -f main.py")
        os.system("python3 main.py")
    else:
        print(f"no update :D (CODE: {update_succes})")
def update_loop():
    while True:
        update_and_run()
        time.sleep(60)
def main_script_monitor():
    while True:
        main_pid = os.popen("pgrep -f main.py").read()
        if not main_pid:
            print("main.py is not running. Restarting...")
            update_and_run()
        time.sleep(10)
if __name__ == "__main__":
    update_thread = threading.Thread(target=update_loop())
    update_thread.start()
    monitor_thread = threading.Thread(target=main_script_monitor())
    monitor_thread.start()
    os.system("python main.py")