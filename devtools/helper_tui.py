# tui_bot.py
import os
import socket
import subprocess
import threading
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

SOCKET_HOST = 'localhost'
SOCKET_PORT = 9920

console = Console()
journal_lines = []
status = "Ready."
input_prompt = "lorelei-bot@localhost: :3># "
lock = threading.Lock()
running = True

def send_command(command: str) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((SOCKET_HOST, SOCKET_PORT))
            client.sendall(command.encode('utf-8'))
            response = client.recv(4096).decode('utf-8')
            return response
    except ConnectionRefusedError:
        return "Connection refused: Is the helper running?"
    except Exception as e:
        return f"Error: {e}"

def get_journal_lines(n=30):
    try:
        result = subprocess.run(  # noqa: S603
            ["journalctl", "-u", "lorelei.service", "-n", str(n), "--no-pager", "--output=short"],  # noqa: E501
            capture_output=True, text=True, check=True,
        )
        return result.stdout.splitlines()
    except Exception as e:
        return [f"Error reading journal: {e}"]

def redraw():
    with lock, console.screen():
        height = console.size.height
        width = console.size.width
        reserved_lines = 2
        journal_height = max(1, height - reserved_lines)
        journal_text = "\n".join(journal_lines[-journal_height:])
        console.print(Panel(journal_text, title="Journal", border_style="grey37"), width=width, height=journal_height)
        console.print(Text(status, style="cyan"), width=width)
        console.print(Text(input_prompt, style="bold"), width=width, end='')

def journal_updater():
    global journal_lines
    while running:
        with lock:
            journal_lines[:] = get_journal_lines(100)
        time.sleep(0.1)

def main():
    global status, running
    # Initial journal fetch
    with lock:
        journal_lines[:] = get_journal_lines(100)
    updater = threading.Thread(target=journal_updater, daemon=True)
    updater.start()
    try:
        while True:
            redraw()  # <-- Only redraw here, in the main thread
            user_input = input()
            if user_input.strip().lower() in ("exit", "quit"):
                break
            with lock:
                status = "Sending..."
            redraw()
            response = send_command(user_input)
            with lock:
                status = response
            redraw()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        running = False
        updater.join(0.2)

if __name__ == "__main__":
    main()
