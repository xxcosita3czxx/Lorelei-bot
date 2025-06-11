# tui_bot.py
import socket
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Input, Log, Static

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

def get_journal_lines(n=100):
    try:
        result = subprocess.run(  # noqa: S603
            ["journalctl", "-u", "lorelei.service", "-n", str(n), "--no-pager", "--output=short"],  # noqa: E501
            capture_output=True, text=True, check=True,
        )
        return result.stdout.splitlines()
    except Exception as e:
        return [f"Error reading journal: {e}"]

class JournalTUI(App):
    CSS = """
    #main_vertical {
        height: 100%;
        layout: vertical;
    }
    #journal {
        height: 1fr;
        border: solid gray;
        padding: 1 1;
    }
    #statusbar {
        height: 1;
        color: cyan;
    }
    #cmd_row {
        height: 3;
    }
    #cmd_input {
        width: 100%;
    }
    """

    status: reactive[str] = reactive("Ready.")

    def compose(self) -> ComposeResult:
        yield Vertical(
            Log(id="journal", highlight=False,auto_scroll=True),
            Static(self.status, id="statusbar",markup=False),
            Horizontal(
                Input(placeholder="Type command and press Enter...", id="cmd_input"),  # noqa: E501
                id="cmd_row",
            ),
            id="main_vertical",
        )

    async def on_mount(self):
        self.query_one("#cmd_input", Input).focus()
        self.set_interval(0.1, self.update_journal)  # 100ms auto-update

    def update_journal(self):
        journal = self.query_one("#journal", Log)
        lines = get_journal_lines()
        if journal.lines != lines:
            journal.clear()
            for line in lines:
                journal.write_line(line)
            journal.scroll_end(animate=False)

    async def on_input_submitted(self, event):
        if event.input.id == "cmd_input":
            cmd = event.input.value
            if cmd.strip():
                if cmd in ("exit", "quit"):
                    self.exit()
                self.status = "Sending..."
                self.query_one("#statusbar", Static).update(self.status)
                self.refresh()
                response = send_command(cmd)
                self.status = response
                self.query_one("#statusbar", Static).update(self.status)
                self.update_journal()
                event.input.value = ""

if __name__ == "__main__":
    JournalTUI().run()
