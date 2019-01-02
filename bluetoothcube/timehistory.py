import os
import kivy

from kivy.factory import Factory
from kivy.clock import Clock

from bluetoothcube.common import Time

from typing import Optional


class TimeHistory(kivy.event.EventDispatcher):
    ao5 = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)
    ao12 = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)
    ao100 = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)

    recent_solves_text = kivy.properties.StringProperty(" ")
    last_time = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)

    def __init__(self):
        # This event can be used to clear time display.
        self.register_event_type('on_time_invalidated')
        super().__init__()
        self.data = []
        self.filepath = None

    def add_time(self, time: Time):
        self.data.append(time)
        self.update_averages()
        self.update_last_time()
        self.update_recent_times()

    def get_last_time(self) -> Time:
        return self.data[-1]

    def update_averages(self):
        self.ao5 = self.get_aon(5)
        self.ao12 = self.get_aon(12)
        self.ao100 = self.get_aon(100)

    def update_last_time(self):
        if len(self.data) < 1:
            self.last_time = None
        else:
            self.last_time = self.data[-1]

    def update_recent_times(self):
        if len(self.data) == 0:
            self.recent_solves_text = ' '
        else:
            T = reversed(self.data[-10:])
            self.recent_solves_text = (
                '  '.join(str(t) for t in T))

    # Computes average of N solves using competition rules.
    def get_aon(self, N) -> Optional[Time]:
        # If there are not enough times recorded, the average is not valid
        if len(self.data) < N:
            return None
        # Get N last times
        t = self.data[-N:]
        # Sort them for easier inspection
        t.sort()
        # Discard best and worst results
        t = t[1:-1]
        # If any DNFs are still on the list, the average is a DNF
        if t[-1].is_dnf():
            return Time('DNF')
        # Finally, compute the average
        average = sum(x.time for x in t)/(N-2)
        return Time(average)

    def mark_last_time(self, state):
        if len(self.data) < 1:
            return
        lt = self.data[-1]
        if state == 'DNF':
            lt.set_dnf(not lt.is_dnf())
        elif state == '+2':
            lt.set_p2(not lt.is_p2())
        elif state == 'OK':
            lt.set_p2(False)
            lt.set_dnf(False)
        self.update_averages()
        self.update_last_time()
        self.update_recent_times()

    def delete_last_time(self, popup=False):
        if popup:
            # Do not actually remove last time, show a popup to request user
            # confirmation.
            Factory.DeleteTimePopup().open()
        else:
            if len(self.data) < 1:
                return
            del self.data[-1]
            self.update_averages()
            self.update_last_time()
            self.update_recent_times()
            self.dispatch('on_time_invalidated')

    def use_file(self, filepath):
        # Load data from file.
        self.data = []
        self.filepath = filepath
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    self.data.append(Time(line))
        except Exception as e:
            # TODO: Backup the previous file, if it exists. Otherwise we'll
            # overwrite it with empty data on the next persist().
            print(f"Failed to load times from {filepath}: {str(e)}")

        self.update_averages()
        self.update_last_time()
        self.update_recent_times()

        # Auto-save every 5 minutes.
        Clock.schedule_interval(lambda td: self.persist(), 60*5)

    def persist(self):
        if not self.filepath:
            return

        print(f"Persisting time history to {self.filepath}")
        try:
            with open(self.filepath, 'w') as f:
                for time in self.data:
                    f.write(time.save() + "\n")
        except Exception as e:
            print(f"Failed to save times to {self.filepath}: {str(e)}")

    def on_time_invalidated(self, *args):
        pass
