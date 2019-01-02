import kivy

from bluetoothcube.patterns import (
    CFOP_CROSS, CFOP_F2L, CFOP_OLL, CFOP_PLL)

from typing import Dict

STAGES = {
    'CFOP': [
        ('CROSS', CFOP_CROSS),
        ('F2L', CFOP_F2L),
        ('OLL', CFOP_OLL),
        ('PLL', CFOP_PLL),
        ('DONE', None)
    ],
}


class Analyzer(kivy.event.EventDispatcher):

    current_stage = kivy.properties.NumericProperty(0)

    def __init__(self, cube, timer):
        super().__init__()

        self.cube = cube
        self.timer = timer

        self.method = 'CFOP'
        self.stages = STAGES[self.method]

        self.cube.bind(on_state_changed=self.on_state_changed)
        self.timer.bind(
            on_solve_started=self.on_solve_started,
            on_solve_ended=self.on_solve_ended)

        self.times: Dict[str, float] = {}
        self.stage_start_time = 0

    def set_method(self, method):
        if method not in STAGES:
            raise NotImplementedError(
                f"Solve method {method} is not known to the analyzer.")

        self.stages = STAGES[method]
        self.method = method
        self.current_stage = 0

        # TBF, it's difficult to define what should happen when method is
        # switched mid-solve.
        self.detect_stage_changes()

    def on_solve_started(self, timer):
        print("CFOP analyzer started")
        self.current_stage = 0
        self.times = {}
        self.stage_start_time = 0
        # Maybe some stages are already complete?
        self.detect_stage_changes()

    def on_state_changed(self, cube, newstate):
        self.detect_stage_changes()

    def detect_stage_changes(self):
        # Advance to next state if target condition is met.
        stage_name, target_pattern = self.stages[self.current_stage]
        if not target_pattern:
            return

        if self.cube.cube_state.toFaceCube().matches_any(target_pattern):
            current_time = self.timer.get_time()
            stage_time = current_time - self.stage_start_time
            print(f"{stage_name} completed in {stage_time:.02f}.")

            self.times[stage_name] = stage_time
            self.stage_start_time = current_time

            self.current_stage += 1

            # Retry - maybe we've advanced more than one stage in one turn?
            self.detect_stage_changes()

    def on_solve_ended(self, timer):
        stage_name, _ = self.stages[self.current_stage]
        if stage_name != 'DONE':
            # Give one more chance for state transition.
            self.detect_stage_changes()
            stage_name, _ = self.stages[self.current_stage]

            if stage_name != 'DONE':
                # Still not completed? Maybe the timer was stopped manually.
                print("Solve analysis invalid, timer was stopped before all "
                      "stages were completed.")
                self.current_stage = len(self.stages - 1)
                self.times = {}
                return

    def get_stage_times(self):
        return self.times
