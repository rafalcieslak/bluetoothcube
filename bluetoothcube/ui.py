import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView

from bluetoothcube.cubedisplay import CubeDisplay  # noqa: F401


class Hideable(kivy.event.EventDispatcher):
    hidden = kivy.properties.BooleanProperty(False)

    def __init__(self):
        super().__init__()
        self.bind(hidden=lambda w, v: self.hide() if v else self.show())

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


# Uses the timer to display measured time.
class TimeDisplay(Label):
    bcolor = kivy.properties.ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.updateevent = None
        app = App.get_running_app()
        app.timer.bind(
            running=self.on_timer_running_changed,
            primed=lambda timer, primed: self.update_bg_color()
        )
        app.timehistory.bind(
            on_time_invalidated=lambda w: self.clear())

        self.timer = app.timer

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
        else:
            self.parent.bcolor = [0, 0, 0, 1]

    def clear(self):
        self.text = "0.0"


# Created dynamically as cubes are discovered.
class CubeButton(AnchorLayout):
    button = kivy.properties.ObjectProperty(None)


# TODO: This class could be defined inline in kv
class DisconnectButton(Button, Hideable):
    def on_press(self):
        App.get_running_app().disconnect_cube()


class CubeStateDisplay(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cube = App.get_running_app().cube
        self.cube.bind(on_state_changed=self.on_cube_state_changed)

    def on_cube_state_changed(self, cube, new_state):
        self.text = '\n'.join(new_state.get_representation_strings())


class HideableLabel(Label, Hideable):
    pass


class HideableButton(Button, Hideable):
    pass


# A scrollview that makes mouse wheel up/down events behave like left/right.
class ScrollViewLR(ScrollView):
    def on_scroll_start(self, touch, check_children=True):
        # Translate up/down scroll events to left/right.
        if hasattr(touch, 'button'):
            if touch.button == 'scrollup':
                touch.button = 'scrollleft'
            if touch.button == 'scrolldown':
                touch.button = 'scrollright'
        # Call original implementation.
        super().on_scroll_start(touch, check_children)


class LastTime(BoxLayout):
    lt = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)


class BluetoothCubeRoot(ScreenManager):
    pass
