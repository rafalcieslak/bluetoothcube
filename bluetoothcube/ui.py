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

        self.timer = app.timer
        self.timehistory = app.timehistory

        self.timer.bind(
            running=self.on_timer_running_changed,
            primed=lambda timer, primed: self.update_bg_color()
        )
        self.timehistory.bind(
            last_time=lambda th, lt: self.update_display(),
            on_time_invalidated=lambda th: self.clear())

    def on_timer_running_changed(self, timer, running):
        if running:
            self.updateevent = Clock.schedule_interval(
                lambda dt: self.update_display(), 0.1)
        else:
            Clock.unschedule(self.updateevent)
        self.update_display()

    def update_display(self):
        if self.timer.running:
            v = self.timer.get_time()
            precision = 1
        else:
            if self.timehistory.last_time:
                v = self.timehistory.last_time.time
            else:
                v = 0
            precision = 2

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


# TODO: This widget is now a bare Label - we could make it richer by using a
# Grid and utilizing partial updates.
class AnalysisDisplay(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.analyzer = App.get_running_app().analyzer
        self.timer = App.get_running_app().timer
        self.timehistory = App.get_running_app().timehistory

        self.analyzer.bind(
            current_stage=lambda a, cs: self.update_display())
        self.timer.bind(
            on_solve_started=self.on_solve_started,
            on_solve_ended=self.on_solve_ended,
            running=lambda t, r: self.update_display())
        self.timehistory.bind(
            last_time=lambda th, lt: self.update_display())

        self.updateevent = None
        self.update_display()

    def on_solve_started(self, timer):
        self.updateevent = Clock.schedule_interval(
            lambda dt: self.update_display(), 0.1)

    def on_solve_ended(self, timer):
        if self.updateevent:
            Clock.unschedule(self.updateevent)

    def update_display(self):
        text = f"Using {self.analyzer.method} analyzer.\n"

        if self.timer.running:
            stages = self.analyzer.get_stage_times()
        else:
            lt = self.timehistory.last_time
            if lt and lt.meta and 'stage_times' in lt.meta:
                text += "Last solve:\n"
                stages = lt.meta['stage_times']
            else:
                stages = []

        for i, v in enumerate(stages):
            stage_name, t = v
            precision = 1 if i+1 == len(stages) else 2
            text += f"[b]{stage_name}[/b]: {t:.0{precision}f}\n"

        self.text = text


# Created dynamically as cubes are discovered.
class CubeButton(AnchorLayout):
    button = kivy.properties.ObjectProperty(None)


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
