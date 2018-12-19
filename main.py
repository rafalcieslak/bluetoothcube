import kivy
import time

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

from btutil.cube import BluetoothCubeScanner, BluetoothCubeConnection


class Hideable:
    def hide(self):
        if hasattr(self, 'saved_attrs'):
            return  # Already hidden
        self.saved_attrs = (self.opacity, self.disabled)
        self.opacity, self.disabled = (0, True)

    def show(self):
        if not hasattr(self, 'saved_attrs'):
            return  # Noe hidden
        self.opacity, self.disabled = self.saved_attrs
        del self.saved_attrs


class TimerButton(Button):
    def on_press(self):
        if self.timedisplay.running:
            self.timedisplay.stop()
        else:
            self.timedisplay.start()


class PrimeButton(Button, Hideable):
    def on_press(self):
        if self.timedisplay.running:
            return
        if self.timedisplay.primed:
            self.timedisplay.unprime()
        else:
            self.timedisplay.prime()


class TimeDisplay(Label):
    # TODO: Split display and timer.
    running = kivy.properties.BooleanProperty(False)
    primed = kivy.properties.BooleanProperty(False)
    measured_time = kivy.properties.NumericProperty(0.0)
    bcolor = kivy.properties.ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
        self.end_time = None
        self.updateevent = None
        self.cube = App.get_running_app().cube
        self.cube.bind(
            on_state_changed=self.on_cube_state_changed,
            solved=self.on_cube_solved_changed)

    def prime(self):
        if self.primed:
            return
        print("Priming timer")
        self.primed = True
        self.update_bg_color()

    def unprime(self):
        if not self.primed:
            return
        self.primed = False
        self.update_bg_color()

    def start(self):
        if self.running:
            return
        self.measured_time = 0.0
        self.start_time = time.time()
        self.updateevent = Clock.schedule_interval(
            self.update_display_clock, 0.1)
        self.running = True
        self.unprime()

        self.update_display()
        self.update_bg_color()

    def stop(self):
        if not self.running:
            return
        self.measured_time = time.time() - self.start_time
        Clock.unschedule(self.updateevent)
        self.running = False
        self.update_display()

    def on_cube_state_changed(self, cube, newstate):
        if self.primed:
            self.start()

    def on_cube_solved_changed(self, cube, solved):
        if solved:
            if self.running:
                self.stop()
        self.update_bg_color()

    def update_display_clock(self, dt):
        self.update_display()

    def update_display(self):
        if self.running:
            v = time.time() - self.start_time
            self.text = f"{v:0.1f}"
        else:
            v = self.measured_time
            self.text = f"{v:0.2f}"

    def update_bg_color(self):
        if self.primed:
            self.bcolor = [0.4, 0, 0, 1]
        elif self.cube.solved:
            self.bcolor = [0, 0.4, 0, 1]
        else:
            self.bcolor = [0, 0, 0, 1]


class CubeButton(AnchorLayout):
    button = kivy.properties.ObjectProperty(None)


class DisconnectButton(Button, Hideable):
    def on_press(self):
        App.get_running_app().disconnect_cube()


class BluetoothCubeRoot(ScreenManager):
    pass


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


MOVES = ['none', 'blue', 'yellow', 'orange', 'white', 'red', 'green']


class CubeState:
    def __init__(self, giiker_state=None):
        self.c = tuple(range(1, 9))   # Corner permutation
        self.co = tuple([3] * 8)      # Corner orientations
        self.e = tuple(range(1, 13))  # Edge permutation
        self.eo = tuple([0] * 12)     # Edge orientations

        if giiker_state:
            s = giiker_state
            self.c = (s[0] >> 4 & 0xF, s[0] >> 0 & 0xF,
                      s[1] >> 4 & 0xF, s[1] >> 0 & 0xF,
                      s[2] >> 4 & 0xF, s[2] >> 0 & 0xF,
                      s[3] >> 4 & 0xF, s[3] >> 0 & 0xF)
            self.co = (s[4] >> 4 & 0xF, s[4] >> 0 & 0xF,
                       s[5] >> 4 & 0xF, s[5] >> 0 & 0xF,
                       s[6] >> 4 & 0xF, s[6] >> 0 & 0xF,
                       s[7] >> 4 & 0xF, s[7] >> 0 & 0xF)
            self.e = (s[8] >> 4 & 0xF, s[8] >> 0 & 0xF,
                      s[9] >> 4 & 0xF, s[9] >> 0 & 0xF,
                      s[10] >> 4 & 0xF, s[10] >> 0 & 0xF,
                      s[11] >> 4 & 0xF, s[11] >> 0 & 0xF,
                      s[12] >> 4 & 0xF, s[12] >> 0 & 0xF,
                      s[13] >> 4 & 0xF, s[13] >> 0 & 0xF)
            self.eo = (s[14] >> 7 & 1, s[14] >> 6 & 1,
                       s[14] >> 5 & 1, s[14] >> 4 & 1,
                       s[14] >> 3 & 1, s[14] >> 2 & 1,
                       s[14] >> 1 & 1, s[14] >> 0 & 1,
                       s[15] >> 7 & 1, s[15] >> 6 & 1,
                       s[15] >> 5 & 1, s[15] >> 4 & 1)

    def __eq__(self, other):
        return (self.c == other.c and self.co == other.co and
                self.e == other.e and self.eo == other.eo)

    def is_solved(self):
        return (self.c == tuple(range(1, 9)) and
                self.co == tuple([3] * 8) and
                self.e == tuple(range(1, 13)) and
                self.eo == tuple([0] * 12))

    def get_representation_strings(self):
        return (' '.join(str(c) for c in self.c),
                ' '.join(str(co) for co in self.co),
                ' '.join(str(e) for e in self.e),
                ' '.join(str(eo) for eo in self.eo), )


class BluetoothCube(kivy.event.EventDispatcher):
    solved = kivy.properties.BooleanProperty(False)

    def __init__(self):
        self.register_event_type('on_state_changed')
        super(BluetoothCube, self).__init__()
        self.cube_state = CubeState()
        self.connection = None

    def set_connection(self, connection):
        self.connection = connection
        self.cube_state = CubeState()
        self.connection.bind(on_state_updated=self.process_state_update)

    def process_state_update(self, connection, state):
        cube_state = CubeState(state)

        move1 = (MOVES[(state[16] >> 4) & 0x0F] +
                 ("" if (state[16] & 0x0F) == 1 else "'"))
        move2 = (MOVES[(state[17] >> 4) & 0x0F] +
                 ("" if (state[17] & 0x0F) == 1 else "'"))
        move3 = (MOVES[(state[18] >> 4) & 0x0F] +
                 ("" if (state[18] & 0x0F) == 1 else "'"))
        move4 = (MOVES[(state[19] >> 4) & 0x0F] +
                 ("" if (state[19] & 0x0F) == 1 else "'"))

        corner_pos, corner_ori, edge_pos, edge_ori = \
            cube_state.get_representation_strings()
        moves = f"{move4} {move3} {move2} {move1}"

        print(f"{corner_pos}  {corner_ori}  {edge_pos}  {edge_ori}  {moves}")

        root = App.get_running_app().root
        root.ids["moves"].text = moves

        self.cube_state = cube_state
        self.solved = cube_state.is_solved()
        self.dispatch('on_state_changed', self.cube_state)

    def on_state_changed(self, *args):
        pass


if __name__ == '__main__':
    BluetoothCubeApp().run()
