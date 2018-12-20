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
            return  # Not hidden
        self.opacity, self.disabled = self.saved_attrs
        del self.saved_attrs


class TimerButton(Button):
    def on_press(self):
        timer = App.get_running_app().timer
        if timer.running:
            timer.stop()
        else:
            timer.start()


class PrimeButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = App.get_running_app().timer
        # self.timer.bind(primed=on_timer_primed)

    def on_press(self):
        if self.timer.primed:
            self.timer.unprime()
        else:
            self.timer.prime()


# Uses both cube and timer to display measured time and cube solved state.
class TimeDisplay(Label):
    bcolor = kivy.properties.ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.updateevent = None
        self.cube = App.get_running_app().cube
        self.cube.bind(
            solved=lambda c, n: self.update_bg_color())
        self.timer = App.get_running_app().timer
        self.timer.bind(
            running=self.on_timer_running_changed,
            primed=lambda timer, primed: self.update_bg_color()
        )

    def on_timer_running_changed(self, timer, running):
        if running:
            self.updateevent = Clock.schedule_interval(
                lambda dt: self.update_display(), 0.1)
        else:
            Clock.unschedule(self.updateevent)
        self.update_display()

    def update_display(self):
        v = self.timer.get_time()
        precision = 1 if self.timer.running else 2
        self.text = f"{v:0.{precision}f}"

    def update_bg_color(self):
        if self.timer.primed:
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
