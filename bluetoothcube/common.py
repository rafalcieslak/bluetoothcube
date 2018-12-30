class Time:
    def __init__(self, time):
        if isinstance(time, float):
            self.dnf = False
            self.p2 = False
            self.time = time
        elif time == 'DNF':
            self.dnf = True
            self.p2 = False
            self.time = None
        else:
            raise ValueError(f"Invalid time {str(time)}")

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
