from textual.app import ComposeResult
from textual.widgets import Input, Log
from textual.containers import Vertical
from textual.screen import Screen
import serial
import serial.tools.list_ports
from textual.widgets import Footer


class MonitorScreen(Screen):
    BINDINGS = [("tab", "toggle_focus", "Toggle focus")]

    def __init__(
        self,
        port: str,
        baud_rate: int,
    ) -> None:
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.serial_port = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Log(highlight=True, id="output_log"),
            Input(placeholder="Type command and press Enter...", id="input_box"),
        )
        yield Footer()

    async def on_mount(self) -> None:
        try:
            self.serial_port = serial.Serial(
                self.port, baudrate=self.baud_rate, timeout=1
            )
            self.set_interval(0.1, self.read_serial)
            self.query_one(Log).write_line(f"Connected to {self.port}")
            self.query_one(Input).focus()
        except serial.SerialException as e:
            self.query_one(Log).write_line(f"[red]Serial error: {e}[/red]")

    async def on_unmount(self) -> None:
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None

    async def read_serial(self):
        try:
            if self.serial_port and self.serial_port.in_waiting:
                data = self.serial_port.readline().decode(errors="ignore").strip()
                if data:
                    self.query_one(Log).write_line(data)
        except:  # noqa: E722
            return None

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text and self.serial_port:
            try:
                self.serial_port.write((text + "\n").encode())
                self.query_one(Log).write_line(f"> {text}")
            except serial.SerialException as e:
                self.query_one(Log).write_line(f"[red]Write error: {e}[/red]")
        event.input.value = ""

    async def on_shutdown(self) -> None:
        if self.serial_port:
            self.serial_port.close()

    def action_toggle_focus(self) -> None:
        input_box = self.query_one(Input)
        log = self.query_one(Log)
        if self.focused is input_box:
            log.focus()
        else:
            input_box.focus()
