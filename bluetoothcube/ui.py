import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = App.get_running_app().timer
        self.just_stopped = False

    def on_press(self):
        self.just_stopped = False
        if self.timer.running:
            self.timer.stop()
            self.just_stopped = True

    def on_release(self):
        if not self.timer.running and not self.just_stopped:
            self.timer.start()


class PrimeButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = App.get_running_app().timer

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

        if v >= 100:
            self.time_text_ratio = 0.25
        else:
            self.time_text_ratio = 0.38

    def update_bg_color(self):
        if self.timer.primed:
            self.parent.bcolor = [0.4, 0, 0, 1]
        elif self.cube.solved:
            self.parent.bcolor = [0, 0.4, 0, 1]
        else:
            self.parent.bcolor = [0, 0, 0, 1]


# Created dynamically as cubes are discovered.
class CubeButton(AnchorLayout):
    button = kivy.properties.ObjectProperty(None)


class DisconnectButton(Button, Hideable):
    def on_press(self):
        App.get_running_app().disconnect_cube()


class BluetoothCubeRoot(ScreenManager):
    pass


class CubeStateDisplay(BoxLayout, Hideable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cube = App.get_running_app().cube
        self.cube.bind(on_state_changed=self.on_cube_state_changed)

    def on_cube_state_changed(self, cube, new_state):
        corner_pos, corner_ori, edge_pos, edge_ori = \
            new_state.get_representation_strings()

        self.corner_pos.text = corner_pos
        self.corner_ori.text = corner_ori
        self.edge_pos.text = edge_pos
        self.edge_ori.text = edge_ori
