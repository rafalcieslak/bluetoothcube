from kociemba.pykociemba.cubiecube import CubieCube as KCubieCube


# Extend CubieCube implementation with our custom mechanisms.
class CubieCube(KCubieCube):
    def __init__(self, **kwargs):
        if 'giiker_state' in kwargs:
            s = kwargs['giiker_state']
            self.cp = [(s[0] >> 4 & 0xF) - 1, (s[0] >> 0 & 0xF) - 1,
                       (s[1] >> 4 & 0xF) - 1, (s[1] >> 0 & 0xF) - 1,
                       (s[2] >> 4 & 0xF) - 1, (s[2] >> 0 & 0xF) - 1,
                       (s[3] >> 4 & 0xF) - 1, (s[3] >> 0 & 0xF) - 1]
            self.co = [(s[4] >> 4 & 0xF) % 3, (s[4] >> 0 & 0xF) % 3,
                       (s[5] >> 4 & 0xF) % 3, (s[5] >> 0 & 0xF) % 3,
                       (s[6] >> 4 & 0xF) % 3, (s[6] >> 0 & 0xF) % 3,
                       (s[7] >> 4 & 0xF) % 3, (s[7] >> 0 & 0xF) % 3]
            self.ep = [(s[8] >> 4 & 0xF) - 1, (s[8] >> 0 & 0xF) - 1,
                       (s[9] >> 4 & 0xF) - 1, (s[9] >> 0 & 0xF) - 1,
                       (s[10] >> 4 & 0xF) - 1, (s[10] >> 0 & 0xF) - 1,
                       (s[11] >> 4 & 0xF) - 1, (s[11] >> 0 & 0xF) - 1,
                       (s[12] >> 4 & 0xF) - 1, (s[12] >> 0 & 0xF) - 1,
                       (s[13] >> 4 & 0xF) - 1, (s[13] >> 0 & 0xF) - 1]
            self.eo = [s[14] >> 7 & 1, s[14] >> 6 & 1,
                       s[14] >> 5 & 1, s[14] >> 4 & 1,
                       s[14] >> 3 & 1, s[14] >> 2 & 1,
                       s[14] >> 1 & 1, s[14] >> 0 & 1,
                       s[15] >> 7 & 1, s[15] >> 6 & 1,
                       s[15] >> 5 & 1, s[15] >> 4 & 1]
        else:
            # Use standard constructor
            super().__init__(**kwargs)

    def __eq__(self, other):
        return (self.cp == other.cp and self.co == other.co and
                self.ep == other.ep and self.eo == other.eo)

    def is_solved(self):
        return (self.cp == tuple(range(1, 9)) and
                self.co == tuple([0] * 8) and
                self.ep == tuple(range(1, 13)) and
                self.eo == tuple([0] * 12))

    def get_representation_strings(self):
        return (' '.join(str(cp) for cp in self.cp),
                ' '.join(str(co) for co in self.co),
                ' '.join(str(ep) for ep in self.ep),
                ' '.join(str(eo) for eo in self.eo), )
