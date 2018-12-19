import kivy
import time

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock


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
