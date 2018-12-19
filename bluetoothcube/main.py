import kivy

from kivy.app import App
from kivy.clock import Clock

from bluetoothcube.btutil.cube import (
    BluetoothCubeScanner, BluetoothCubeConnection)

from bluetoothcube.bluetoothcube import BluetoothCube
from .ui import CubeButton, BluetoothCubeRoot


class BluetoothCubeApp(App):
    counter = kivy.properties.NumericProperty(0)
    cubelist = kivy.properties.ObjectProperty(None)

    def __init__(self):
        super(BluetoothCubeApp, self).__init__()

        self.cube_scanner = BluetoothCubeScanner()
        self.cube_scanner.bind(on_cube_found=self.on_cube_found)

        self.cube_connection = BluetoothCubeConnection()
        self.cube_connection.bind(
            on_cube_connecting=self.on_cube_connecting,
            on_cube_connecting_failed=self.on_cube_connecting_failed,
            on_cube_connected=self.on_cube_ready,
            on_cube_disconnected=self.on_cube_disconnected
            )

        self.cube = BluetoothCube()
        self.cube.bind(on_state_changed=self.on_cube_state_changed)

        self.show_cancel_button = None
        self.cube_buttons = []

        # When the app starts, start a scan.
        Clock.schedule_once(lambda td: self.start_scan(), 1)

    def build(self):
        return BluetoothCubeRoot()

    def start_scan(self):
        print("Starting a scan...")

        for button in self.cube_buttons:
            self.root.cubelist.remove_widget(button)
        self.cube_buttons = []

        self.cube_scanner.scan()

    def on_cube_found(self, scanner, device):
        print("Found a GiiKER Cube.")

        button = CubeButton()
        button.button.text = device.getName()
        self.cube_buttons.append(button)
        button.button.bind(
            on_press=lambda b: self.on_cube_button_pressed(device))
        self.root.cubelist.add_widget(button, index=len(self.cube_buttons))

    def on_cube_button_pressed(self, device):
        print("Connecting to a cube...")

        self.root.transition.direction = 'left'
        self.root.current = 'connecting'

        self.root.connecting_cancelbutton.hide()

        if self.show_cancel_button:
            Clock.unschedule(self.show_cancel_button)
        self.show_cancel_button = Clock.schedule_once(
            lambda td:
            self.root.connecting_cancelbutton.show(), 10)

        # Calling this directly would freeze UI for a fraction of a second.
        Clock.schedule_once(lambda td: self.cube_connection.connect(device))

    def on_cube_connecting(self, connection, message, percent):
        self.root.connecting_label.text = message
        self.root.connecting_label.color = [1, 1, 1, 1]
        self.root.connecting_progressbar.value = percent

    def on_cube_connecting_failed(self, connection, message):
        self.root.connecting_label.text = message
        self.root.connecting_label.color = [1, 0.2, 0.2, 1]
        self.root.connecting_cancelbutton.show()

    def on_cube_ready(self, cube_connection):
        print("Cube ready!")
        self.cube.set_connection(self.cube_connection)

        self.root.transition.direction = 'left'
        self.root.current = 'timer'

    def on_cube_disconnected(self, connection):
        self.goto_cube_selection()

    def disconnect_cube(self):
        self.cube_connection.disconnect()
        self.goto_cube_selection()

    def goto_cube_selection(self):
        self.root.transition.direction = 'right'
        self.root.current = 'cube-selection'
        self.start_scan()

    def on_cube_state_changed(self, cube, new_state):
        corner_pos, corner_ori, edge_pos, edge_ori = \
            new_state.get_representation_strings()
        # TODO: These might be properties.
        self.root.ids["corner_pos"].text = corner_pos
        self.root.ids["corner_ori"].text = corner_ori
        self.root.ids["edge_pos"].text = edge_pos
        self.root.ids["edge_ori"].text = edge_ori
