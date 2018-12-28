class Time:
    def __init__(self, time):
        if isinstance(time, float):
            self.dnf = False
            self.time = time
        elif time == 'DNF':
            self.dnf = True
            self.time = None
        else:
            raise ValueError(f"Invalid time {str(time)}")

    def is_dnf(self) -> bool:
        return self.dnf

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
        return f"{self.time:.02f}"
