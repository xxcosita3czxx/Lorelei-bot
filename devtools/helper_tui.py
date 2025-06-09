# tui_bot.py
import asyncio
import socket
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Static

SOCKET_HOST = 'localhost'
SOCKET_PORT = 9920

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
    except subprocess.CalledProcessError as e:
        return [f"Journalctl error: {e}", f"{e.output if hasattr(e, 'output') else ''}"]  # noqa: E501
    except FileNotFoundError:
        return ["journalctl not found. Is systemd available on this system?"]
    except Exception as e:
        return [f"Error reading journal: {e}"]

class BotTUI(App):
    CSS = """
    #main_vertical {
        height: 100%;
        layout: vertical;
    }

    #journal {
        height: 90fr;
        overflow-y: scroll;
        border: solid gray;
        padding: 1 1;
    }

    #statusbar {
        height: 1;
        color: cyan;
    }

    #cmd_input {
        height: 5;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("\n".join(get_journal_lines()), id="journal", markup=False),
            Static("Ready.", id="statusbar"),
            Horizontal(
                Input(placeholder="Type command and press Enter...", id="cmd_input"),  # noqa: E501
            ),
            id="main_vertical",
        )

    async def on_mount(self):
        self.query_one("#cmd_input", Input).focus()

    def update_journal(self):
        self.query_one("#journal", Static).update(
            "\n".join(get_journal_lines()),
        )

    async def on_input_submitted(self, event):
        if event.input.id == "cmd_input":
            cmd = event.input.value
            if cmd.strip():
                self.query_one("#statusbar", Static).update("Sending...")
                await asyncio.sleep(0)
                response = send_command(cmd)
                self.query_one("#statusbar", Static).update(response)
                self.update_journal()
                event.input.value = ""

if __name__ == "__main__":
    BotTUI().run()
