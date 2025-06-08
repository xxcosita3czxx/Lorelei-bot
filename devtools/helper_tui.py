# tui_bot.py
import asyncio
import socket
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Static, TextLog  # type: ignore

SOCKET_HOST = 'localhost'
SOCKET_PORT = 9920

def send_command(command: str) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((SOCKET_HOST, SOCKET_PORT))
            client.sendall(command.encode('utf-8'))
            response = client.recv(4096).decode('utf-8')
            return response
    except Exception as e:
        return f"Error: {e}"

def get_journal_lines(n=30):
    try:
        # Change 'your-bot.service' to your actual service name if needed
        result = subprocess.run(  # noqa: S603
            ["journalctl", "-u", "lorelei.service", "-n", str(n), "--no-pager", "--output=short"],  # noqa: E501
            capture_output=True, text=True,
        )
        return result.stdout
    except Exception as e:
        return f"Error reading journal: {e}"

class BotTUI(App):
    CSS_PATH = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            TextLog(highlight=False, id="journal"),
            Static("Ready.", id="statusbar"),
            Horizontal(
                Input(placeholder="Type command and press Enter...", id="cmd_input"),  # noqa: E501
            ),
        )

    async def on_mount(self):
        await self.query_one("#cmd_input", Input).focus() # type: ignore
        # Fill the log on start
        self.query_one("#journal", TextLog).write(get_journal_lines())

    async def on_input_submitted(self, event):
        if event.input.id == "cmd_input":
            cmd = event.input.value
            if cmd.strip():
                self.query_one("#statusbar", Static).update("Sending...")
                await asyncio.sleep(0)
                response = send_command(cmd)
                self.query_one("#statusbar", Static).update(response)
                # Refresh journal
                journal = self.query_one("#journal", TextLog)
                journal.clear()
                journal.write(get_journal_lines())
                event.input.value = ""

if __name__ == "__main__":
    BotTUI().run()
