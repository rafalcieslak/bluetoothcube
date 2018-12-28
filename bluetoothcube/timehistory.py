import kivy

from bluetoothcube.common import Time

from typing import Optional


class TimeHistory(kivy.event.EventDispatcher):
    last_time = kivy.properties.NumericProperty(None)
    ao5 = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)
    ao12 = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)
    ao100 = kivy.properties.ObjectProperty(
        None, allownone=True, force_dispatch=True)

    def __init__(self):
        self.data = []

    def add_time(self, time: Time):
        self.data.append(time)
        self.update_averages()

    def get_last_time(self) -> Time:
        return self.data[-1]

    def update_averages(self):
        self.ao5 = self.get_aon(5)
        self.ao12 = self.get_aon(12)
        self.ao100 = self.get_aon(100)

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
