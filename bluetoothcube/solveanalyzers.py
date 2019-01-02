import kivy

from bluetoothcube.patterns import (
    CFOP_CROSS, CFOP_F2L, CFOP_OLL, CFOP_PLL)

from typing import Dict


class CFOPAnalyzer(kivy.event.EventDispatcher):
    STAGES = ['CROSS', 'F2L', 'OLL', 'PLL', 'DONE']
    STAGE_COMPLETION_CONDITIONS = {
        'CROSS': CFOP_CROSS,
        'F2L': CFOP_F2L,
        'OLL': CFOP_OLL,
        'PLL': CFOP_PLL}

    current_stage = kivy.properties.StringProperty('DONE')

    def __init__(self, cube, timer):
        super().__init__()

        self.cube = cube
        self.timer = timer

        self.cube.bind(on_state_changed=self.on_state_changed)
        self.timer.bind(
            on_solve_started=self.on_solve_started,
            on_solve_ended=self.on_solve_ended)

        self.times: Dict[CFOPAnalyzer.Stage, float] = {}
        self.stage_start_time = 0

    def on_solve_started(self, timer):
        print("CFOP analyzer started")
        self.current_stage = self.STAGES[0]
        self.times = {}
        self.stage_start_time = 0
        # Maybe some stages are already complete?
        self.detect_stage_changes()

    def on_state_changed(self, cube, newstate):
        self.detect_stage_changes()

    def detect_stage_changes(self):
        # Advance to next state if target condition is met.
        target_pattern = self.STAGE_COMPLETION_CONDITIONS.get(
            self.current_stage, None)
        if not target_pattern:
            return

        if self.cube.cube_state.toFaceCube().matches_any(target_pattern):
            current_time = self.timer.get_time()
            stage_time = current_time - self.stage_start_time
            print(f"{self.current_stage} completed in {stage_time:.02f}.")

            self.times[self.current_stage] = stage_time
            self.stage_start_time = current_time

            self.current_stage = self.STAGES[
                1 + self.STAGES.index(self.current_stage)]

            # Retry - maybe we've advanced more than one stage in one turn?
            self.detect_stage_changes()

    def on_solve_ended(self, timer):
        if self.current_stage != 'DONE':
            # Give one more chance for state transition.
            self.detect_stage_changes()

            if self.current_stage != 'DONE':
                # Still not completed? Maybe the timer was stopped manually.
                print("Solve analysis invalid, timer was stopped before all "
                      "stages were completed.")
                self.current_stage = 'INVALID'
                self.times = {}
                return

    def get_stage_times(self):
        return self.times
