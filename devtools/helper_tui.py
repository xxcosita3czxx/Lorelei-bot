# tui_bot.py
import os
import socket
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

SOCKET_HOST = 'localhost'
SOCKET_PORT = 9920

console = Console()

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

def redraw(journal_lines, status, input_prompt):
    # Get terminal size
    height = console.size.height
    width = console.size.width

    # Reserve 2 lines for status and input
    reserved_lines = 2
    journal_height = max(1, height - reserved_lines)
    journal_text = "\n".join(journal_lines[-journal_height:])

    os.system('clear')  # noqa: S605
    console.print(Panel(journal_text, title="Journal", border_style="grey37"), width=width, height=journal_height)  # noqa: E501
    console.print(Text(status, style="cyan"), width=width)
    console.print(Text(input_prompt, style="bold"), width=width, end='')

def main():
    status = "Ready."
    input_prompt = "lorelei-bot@localhost: :3># "
    journal_lines = get_journal_lines(30)

    while True:
        redraw(journal_lines, status, input_prompt)
        try:
            user_input = input()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.strip().lower() in ("exit", "quit"):
            break
        status = "Sending..."
        redraw(journal_lines, status, input_prompt + user_input)
        response = send_command(user_input)
        status = response
        journal_lines = get_journal_lines(30)

if __name__ == "__main__":
    main()
