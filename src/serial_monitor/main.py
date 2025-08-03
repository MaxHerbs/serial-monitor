from typing import cast
from textual.app import App
from textual.widgets import Button
from textual.containers import Vertical

from serial_monitor.Monitor import MonitorScreen
from serial_monitor.PortSelector import PortSelectScreen, PortSelected


class SerialMonitorApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    Log {
        height: 1fr;
        border: solid green;
    }
    Input {
        height: 3;
        border: solid blue;
    }
    """

    BINDINGS = [
        ("tab", "toggle_focus", "Toggle focus"),
        ("escape", "go_back", "Select serial port"),
    ]

    def on_mount(self) -> None:
        select_screen = PortSelectScreen()
        self.install_screen(select_screen, name="port_select")
        self.push_screen(select_screen)

    async def on_port_selected(self, message: PortSelected) -> None:
        if self.is_screen_installed("monitor"):
            self.uninstall_screen("monitor")

        monitor_screen = MonitorScreen(message.port, message.baud_rate)
        self.install_screen(monitor_screen, name="monitor")
        await self.push_screen(monitor_screen)

    async def action_go_back(self) -> None:
        await self.pop_screen()

        if self.is_screen_installed("monitor"):
            self.uninstall_screen("monitor")

        port_select_screen = cast(PortSelectScreen, self.get_screen("port_select"))
        await port_select_screen.update_ports()

        if self.screen_stack[-1].name != "port_select":
            await self.push_screen(port_select_screen)

        container = port_select_screen.query_one("#port_container", Vertical)
        first_button = container.query(Button).first()
        if first_button:
            first_button.focus()


def main():
    SerialMonitorApp().run()


if __name__ == "__main__":
    main()
