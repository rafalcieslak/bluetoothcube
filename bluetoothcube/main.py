import os
import kivy

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import Metrics
from kivy.core.window import Window

import kociemba

from bluetoothcube.btutil import (
    BluetoothCubeScanner, BluetoothCubeConnection)

from bluetoothcube.bluetoothcube import BluetoothCube, ScrambleDetector
from bluetoothcube.ui import CubeButton, BluetoothCubeRoot
from bluetoothcube.timer import Timer
from bluetoothcube.timehistory import TimeHistory


if kivy.platform == "linux":
    # Some configuration specific to the desktop (windowed) version of the app.

    # Kivy does not detect DPI on linux, it's hardcoded to 96. Which is
    # bonkers, one of the primary reasons why people use kivy is because it
    # correctly scales interfaces and layouts.
    # TODO: Detect and configure DPI.

    # Disable right-click simulation for multi-touch.
    kivy.config.Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class BluetoothCubeApp(App):
    cubelist = kivy.properties.ObjectProperty(None)

    def __init__(self):
        super(BluetoothCubeApp, self).__init__()

        if kivy.platform == "linux":
            # Some configuration specific to the desktop (windowed) version of the app.

            # If using default window size...
            if Window.size == (800, 600):
                print("Default window size, switching to custom")
                # Switch to a nicer shape
                width, height = 540, 960  # FHD/2 portait
                # if Metrics.density >= 2:
                #     width, height = width * 2, height * 2
                Window.size = (width, height)

        print(f"Density: {Metrics.density}")
        print(f"DPI: {Metrics.dpi}")

        self.cube_scanner = BluetoothCubeScanner()
        self.cube_scanner.bind(
            on_cube_found=self.on_cube_found,
            on_paired_cube_found=self.on_paired_cube_found)

        self.cube_connection = None

        self.cube = BluetoothCube()

        self.show_cancel_button = None
        self.cube_buttons = []

        self.timehistory = TimeHistory()

        self.timer = Timer(self.cube)
        self.timer.bind(on_new_time=self.on_new_time)

        self.scrambledetector = ScrambleDetector(self.cube)
        self.scrambledetector.bind(
            on_manual_scramble_finished=lambda sd: self.autoprime())

        # When the app starts, start a scan.
        Clock.schedule_once(lambda td: self.start_scan(), 1)

        # When the app starts, load time history from file.
        Clock.schedule_once(
            lambda td:
            self.timehistory.use_file(
                os.path.join(self.user_data_dir, "times.txt")), 1)

    def build(self):
        return BluetoothCubeRoot()

    def on_stop(self):
        print("Stopping application")

        # Save time history.
        self.timehistory.persist()

        # Make sure to disassociate the cube when closing the app.
        # Otherwise other devices won't connect.
        if self.cube_connection:
            self.cube_connection.disconnect()

    def start_scan(self):
        print("Starting a scan...")

        for button in self.cube_buttons:
            self.root.cubelist.remove_widget(button)
        self.cube_buttons = []

        self.cube_scanner.scan()

    def on_cube_found(self, scanner, device):
        print("Found a GiiKER Cube.")

        button = CubeButton()
        button.button.text = device.name
        self.cube_buttons.append(button)
        button.button.bind(
            on_press=lambda b: self.on_cube_button_pressed(device))
        self.root.cubelist.add_widget(button, index=len(self.cube_buttons))

    def on_paired_cube_found(self, scanner, deviceinfo):
        print("Found a PAIRED GiiKER Cube.")

        # Do not build UI, connect immediately.
        self.connect_to_cube(deviceinfo)

    def on_cube_button_pressed(self, deviceinfo):
        self.connect_to_cube(deviceinfo)

    def connect_to_cube(self, deviceinfo):
        print("Connecting to a cube...")

        self.cube_scanner.stop_scan()

        self.root.transition.direction = 'left'
        self.root.current = 'connecting'

        self.root.connecting_cancelbutton.hide()

        if self.show_cancel_button:
            Clock.unschedule(self.show_cancel_button)
        self.show_cancel_button = Clock.schedule_once(
            lambda td:
            self.root.connecting_cancelbutton.show(), 10)

        self.cube_connection = BluetoothCubeConnection(deviceinfo)
        self.cube_connection.bind(
            on_cube_connecting=self.on_cube_connecting,
            on_cube_connecting_failed=self.on_cube_connecting_failed,
            on_cube_connected=self.on_cube_ready,
            on_cube_disconnected=self.on_cube_disconnected
            )

        # Calling this directly might freeze UI for a moment
        Clock.schedule_once(lambda td: self.cube_connection.connect())

    def continue_without_cube(self):
        self.cube.disable_connection()
        self.root.disconnectbutton.text = "Connect a cube"
        self.root.transition.direction = 'left'
        self.root.current = 'timer'

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

        self.root.disconnectbutton.text = "Disconnect cube"
        self.root.transition.direction = 'left'
        self.root.current = 'timer'

    def on_cube_disconnected(self, connection):
        self.goto_cube_selection()
        self.start_scan()

    def disconnect_cube(self):
        if self.cube_connection:
            self.cube_connection.disconnect()
        self.goto_cube_selection()

    def goto_cube_selection(self):
        self.root.transition.direction = 'right'
        self.root.current = 'cube-selection'

    # Triggered when the timer records a new time.
    def on_new_time(self, timer, time):
        self.timehistory.add_time(time)

    # Called when used pressed the "reset cube" button.
    def reset_cube(self, popup=True):
        if not self.cube_connection:
            return

        if popup:
            # Do not actually reset the cube, just show a popup to request user
            # confirmation.
            Factory.ResetCubePopup().open()
        else:
            self.cube_connection.reset_cube()

    def solve(self):
        cube_str = self.cube.cube_state.toFaceCube().to_String()

        if self.cube.cube_state.is_solved():
            solution = "Cube is already solved!"
        else:
            try:
                print("Solving...")
                solution = kociemba.solve(cube_str)
                print(f"Solution: {solution}")
            except ValueError as e:
                print(f"Failed to solve the cube: {str(e)}")
                return

        solution_popup = Factory.SolutionPopup()
        solution_popup.ids["solution_label"].text = solution
        solution_popup.open()

    def autoprime(self):
        if not self.timer.running and not self.timer.primed:
            print("Autoprime.")
            self.timer.prime()
