import kivy
import time

from bluetoothcube.common import Time


class Timer(kivy.event.EventDispatcher):
    running = kivy.properties.BooleanProperty(False)
    primed = kivy.properties.BooleanProperty(False)
    measured_time = kivy.properties.NumericProperty(0.0)

    def __init__(self, cube):
        self.register_event_type('on_solve_started')
        self.register_event_type('on_solve_ended')
        self.register_event_type('on_new_time')
        super().__init__()

        self.start_time = None
        self.end_time = None
        self.measured_time = 0

        self.cube = cube

        self.analyzer = None

        self.cube.bind(
            on_state_changed=self.on_cube_state_changed,
            solved=self.on_cube_solved_changed)

    def use_analyzer(self, analyzer):
        self.analyzer = analyzer

    def prime(self):
        if self.primed or self.running:
            return
        self.primed = True

    def unprime(self):
        if not self.primed or self.running:
            return
        self.primed = False

    def start(self):
        if self.running:
            return
        self.unprime()
        self.start_time = time.time()
        self.measured_time = 0
        self.running = True

        # TODO: This event should probably originate in some other class.
        self.dispatch('on_solve_started')

    def get_time(self) -> float:
        if not self.running:
            return self.measured_time
        return time.time() - self.start_time

    def stop(self):
        if not self.running:
            return
        self.measured_time = time.time() - self.start_time
        self.running = False

        self.dispatch('on_solve_ended')

        new_time = Time(self.measured_time, {
            'stage_times': self.analyzer.get_stage_times()
        })
        print(new_time.meta)

        self.dispatch('on_new_time', new_time)

    def on_cube_state_changed(self, cube, newstate):
        if self.primed:
            self.start()

    def on_cube_solved_changed(self, cube, solved):
        if solved:
            if self.running:
                self.stop()

    def on_solve_started(self):
        pass

    def on_solve_ended(self):
        pass

    def on_new_time(self, time):
        pass
