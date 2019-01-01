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
        self.timer.bind(on_solve_started=self.on_solve_started)

        self.times: Dict[CFOPAnalyzer.Stage, float] = {}
        self.stage_start_time = 0

    def on_solve_started(self, timer):
        print("CFOP analyzer started")
        self.current_stage = self.STAGES[0]
        self.times = {}
        self.stage_start_time = 0

    def on_state_changed(self, cube, newstate):
        # Advance to next state if target condition is met.
        target_pattern = self.STAGE_COMPLETION_CONDITIONS.get(
            self.current_stage, None)
        if not target_pattern:
            return

        if newstate.toFaceCube().matches_any(target_pattern):
            current_time = self.timer.get_time()
            stage_time = current_time - self.stage_start_time
            print(f"{self.current_stage} completed in {stage_time:.02f}.")

            self.times[self.current_stage] = stage_time
            self.stage_start_time = current_time

            self.current_stage = self.STAGES[
                1 + self.STAGES.index(self.current_stage)]

        if self.current_stage == 'DONE':
            print(self.times)

    def complete(self):
        pass
