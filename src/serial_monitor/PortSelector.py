from collections import Counter
from textual.app import ComposeResult
from textual.widgets import Button, Static, Footer, Input
from textual.containers import Vertical
from textual.screen import Screen
from textual.message import Message
import serial
import serial.tools.list_ports


class PortSelected(Message):
    def __init__(self, port: str, baud_rate: int) -> None:
        self.port = port
        self.baud_rate = baud_rate
        super().__init__()


class PortSelectScreen(Screen):
    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("enter", "select", "Select"),
        ("q", "exit", "Exit"),
        ("escape", "exit", "Exit"),
    ]

    CSS = """
    #port_container {
        align-horizontal: center;
        align-vertical: top;
        background: transparent;
        border: none;
        padding: 0;
    }

    #baud_rate {
        width: 15%;
        align-horizontal: center;
        background: transparent;
    }

    #baud_container {
        align-horizontal: center;
        align-vertical: bottom;
        background: transparent;
    }

    Button {
        background: transparent;
        border: none;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Select a serial port:", id="title")
        yield Vertical(id="port_container")
        yield Vertical(
            Input(id="baud_rate", placeholder="Baud Rate"), id="baud_container"
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.port_update_timer = self.set_interval(3, self.update_ports)
        self.previous_ports = []
        await self.update_ports()

    def on_unmount(self) -> None:
        self.port_update_timer.stop()

    def action_cursor_down(self) -> None:
        buttons = list(self.query(Button))
        if not buttons:
            return
        focused = self.focused
        if isinstance(focused, Button) and focused in buttons:
            index = buttons.index(focused)
            next_index = (index + 1) % len(buttons)
            buttons[next_index].focus()
        else:
            buttons[0].focus()

    def action_cursor_up(self) -> None:
        buttons = list(self.query(Button))
        if not buttons:
            return
        focused = self.focused
        if isinstance(focused, Button) and focused in buttons:
            index = buttons.index(focused)
            next_index = (index - 1) % len(buttons)
            buttons[next_index].focus()
        else:
            buttons[0].focus()

    async def action_select(self) -> None:
        self.change_screen()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        self.change_screen()

    def change_screen(self) -> None:
        try:
            baud_rate = int(self.query_one("#baud_rate", Input).value.strip())
            if isinstance(self.focused, Button) and self.focused.name:
                self.post_message(PortSelected(self.focused.name, baud_rate))
        except ValueError:
            self.query_one("#baud_rate", Input).value = "NOT A NUMBER"
            return

    async def action_exit(self) -> None:
        self.app.exit()

    async def update_ports(self) -> None:
        container = self.query_one("#port_container", Vertical)
        ports = [device.device for device in serial.tools.list_ports.comports()]
        if Counter(ports) != Counter(self.previous_ports):
            await container.remove_children()
            for i, port in enumerate(ports):
                safe_id = port.replace("/", "_") + f"_{i}"
                btn = Button(port, id=safe_id, name=port)
                container.mount(btn)
            self.previous_ports = ports

            first_button = container.query(Button).first()
            if first_button:
                first_button.focus()
