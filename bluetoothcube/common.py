import json
import datetime

from bluetoothcube.utils import datetime_from_isoformat


class Time:
    def __init__(self, time, meta=None):
        self.dnf = False
        self.p2 = False
        self.meta = meta
        self.ts = datetime.datetime.utcnow()
        if isinstance(time, float):
            self.time = time
        elif time == 'DNF':
            self.time = None
        elif isinstance(time, str):
            # Parse from string.
            ts, time, meta = time.split('|', 2)
            self.ts = datetime_from_isoformat(ts)
            if time == 'DNF':
                self.time = None
            else:
                if time[-1] == "+":
                    self.p2 = True
                    time = time[:-1]
                self.time = float(time)
            self.meta = meta
        else:
            print(f"ERROR: Invalid time {str(time)}")

        if self.time is None:
            self.dnf = True

    def is_dnf(self) -> bool:
        return self.dnf

    def is_p2(self) -> bool:
        return self.p2

    def set_dnf(self, dnf: bool):
        self.dnf = dnf
        if dnf:
            self.set_p2(False)

    def set_p2(self, p2: bool):
        if p2 == self.p2:
            return
        self.p2 = p2
        if p2:
            self.time += 2
            self.set_dnf(False)
        else:
            self.time -= 2

    def __eq__(self, other):
        if self.dnf:
            return other.dnf
        return self.time == other.time

    def __gt__(self, other):
        if other.dnf:
            return False
        if self.dnf:
            return True
        return self.time > other.time

    def __lt__(self, other):
        if self.dnf:
            return False
        if other.dnf:
            return True
        return self.time < other.time

    def __str__(self) -> str:
        if self.dnf:
            return 'DNF'
        return f"{self.time:.02f}" + ("" if not self.p2 else "+")

    def save(self) -> str:
        return (self.ts.isoformat() + "|" + str(self) + "|" +
                json.dumps(self.meta))
