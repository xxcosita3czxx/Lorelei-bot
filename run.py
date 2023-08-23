import os
import time
import threading
import utils.cosita_toolkit as ctkit
def update_and_run():
    ctkit.update_script_from_github(owner = "xxcosita3czxx", repo = "Cosita-ToolKit", file_path = "cosita_toolkit.py", local_file_path = "./utils/cosita_toolkit.py")
    update_succes = ctkit.update_script_from_github("xxcosita3czxx", "Lorelei-bot", "main.py","./main.py")
    if update_succes == 1:
        os.system("pkill -f main.py")
        os.system("python3 main.py")
    else:
        print(f"no update :D (CODE: {update_succes})")
def update_loop():
    while True:
        update_and_run()
        time.sleep(60)
if __name__ == "__main__":
    update_thread = threading.Thread(target=update_loop)
    update_thread.start()
    os.system("python main.py")