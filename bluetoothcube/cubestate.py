from kociemba.pykociemba.cubiecube import CubieCube as KCubieCube
from kociemba.pykociemba.facecube import FaceCube as KFaceCube


# CPP permutation transforms corners from giiker coords to kociemba
# coords. ICPP is the inverse permutation
#      0  1  2  3  4  5  6  7
CPP = (1, 2, 6, 5, 0, 3, 7, 4)
iCPP = (4, 0, 1, 5, 7, 3, 2, 6)

# EPP permutation transforms edges from giiker coords to kociemba
# coords. IEPP is the inverse permutation
#      0  1  2  3  4  5  6  7  8  9  10  11
EPP = (5, 2, 6, 10, 4, 0, 7, 8, 1, 3, 11, 9)
iEPP = (5, 8, 1, 9, 4, 0, 2, 6, 7, 11, 3, 10)

# Corner types - clockwise twists going from green/blue sticker to
# white/yellow sticker.
CT = [1, -1, 1, -1, -1, 1, -1, 1]

# Edge types - whether a sticker switch is necessary to go from bgwy sticker
# to wybg sticker.
ET = [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0]

# Which faces is each corner a part of - in giiker orientation order.
COG = ['FUR', 'FUL', 'BUL', 'BUR',
       'FDR', 'FDL', 'BDL', 'BDR']

# Clockwise order of sticker colors - in Kociemba orientation
# order.
COK = ['URF', 'UFL', 'ULB', 'UBR',
       'DFR', 'DLF', 'DBL', 'DRB']

# Which faces is each edge a part of - in giiker orientation order.
EOG = ['UR', 'FU', 'UL', 'BU',
       'DR', 'FD', 'DL', 'BD',
       'FR', 'FL', 'BL', 'BR']

# Which faces is each edge a part of - in Kociemba orientation order.
EOK = ['UR', 'UF', 'UL', 'UB',
       'DR', 'DF', 'DL', 'DB',
       'FR', 'FL', 'BL', 'BR']


# Extend CubieCube implementation with our custom mechanisms.
class CubieCube(KCubieCube):
    def __init__(self, **kwargs):
        if 'giiker_state' in kwargs:
            s = kwargs['giiker_state']

            super().__init__()

            # TODO: I believe this entire algoritm can be reimplemented by
            # getting a CubieCube in Giiker order, converting to a FaceCube,
            # swapping colors from Kociemba color scheme and cube orientation
            # to WCA color scheme and cube orientation, then converting back to
            # a CubieCube. This would also require reading edge data in
            # slightly different order.

            gcp = [(s[0] >> 4 & 0xF) - 1, (s[0] >> 0 & 0xF) - 1,
                   (s[1] >> 4 & 0xF) - 1, (s[1] >> 0 & 0xF) - 1,
                   (s[2] >> 4 & 0xF) - 1, (s[2] >> 0 & 0xF) - 1,
                   (s[3] >> 4 & 0xF) - 1, (s[3] >> 0 & 0xF) - 1]
            gco = [(s[4] >> 4 & 0xF) % 3, (s[4] >> 0 & 0xF) % 3,
                   (s[5] >> 4 & 0xF) % 3, (s[5] >> 0 & 0xF) % 3,
                   (s[6] >> 4 & 0xF) % 3, (s[6] >> 0 & 0xF) % 3,
                   (s[7] >> 4 & 0xF) % 3, (s[7] >> 0 & 0xF) % 3]
            gep = [(s[8] >> 4 & 0xF) - 1, (s[8] >> 0 & 0xF) - 1,
                   (s[9] >> 4 & 0xF) - 1, (s[9] >> 0 & 0xF) - 1,
                   (s[10] >> 4 & 0xF) - 1, (s[10] >> 0 & 0xF) - 1,
                   (s[11] >> 4 & 0xF) - 1, (s[11] >> 0 & 0xF) - 1,
                   (s[12] >> 4 & 0xF) - 1, (s[12] >> 0 & 0xF) - 1,
                   (s[13] >> 4 & 0xF) - 1, (s[13] >> 0 & 0xF) - 1]
            geo = [s[14] >> 7 & 1, s[14] >> 6 & 1,
                   s[14] >> 5 & 1, s[14] >> 4 & 1,
                   s[14] >> 3 & 1, s[14] >> 2 & 1,
                   s[14] >> 1 & 1, s[14] >> 0 & 1,
                   s[15] >> 7 & 1, s[15] >> 6 & 1,
                   s[15] >> 5 & 1, s[15] >> 4 & 1]

            self.cp = [iCPP[gcp[i]] for i in CPP]
            self.ep = [iEPP[gep[i]] for i in EPP]

            for slot in range(0, 8):
                # Get the giiker orientation of this corner
                orig_orient = gco[CPP[slot]]

                # Get the face that g/b sticker is at
                gb_direction = COG[slot][orig_orient]

                # Find the clockwise twists wrg. the g/b sticker
                gb_index = COK[slot].index(gb_direction)

                # Go from g/b sticker to w/y sticker
                cubie = self.cp[slot]
                wy_index = (gb_index + CT[cubie]) % 3

                self.co[slot] = wy_index

            for slot in range(0, 12):
                # Get the giiker orientation of this edge
                orig_orient = geo[EPP[slot]]

                # Get the face that r/o/b/g sticker is at
                bgwy_direction = EOG[slot][orig_orient]

                # Find the clockwise twists wrg. the g/b sticker
                bgwy_index = EOK[slot].index(bgwy_direction)

                # Go from r/o/b/g sticker to w/y/b/g sticker
                cubie = self.ep[slot]
                wybg_index = (bgwy_index + ET[cubie]) % 2

                self.eo[slot] = wybg_index

        else:
            # Use standard constructor
            super().__init__(**kwargs)

    def __eq__(self, other):
        return (self.cp == other.cp and self.co == other.co and
                self.ep == other.ep and self.eo == other.eo)

    def is_solved(self):
        return (self.cp == list(range(0, 8)) and
                self.co == list([0] * 8) and
                self.ep == list(range(0, 12)) and
                self.eo == list([0] * 12))

    def get_representation_strings(self):
        return [' '.join(str(cp) for cp in self.cp),
                ' '.join(str(co) for co in self.co),
                ' '.join(str(ep) for ep in self.ep),
                ' '.join(str(eo) for eo in self.eo), ]


class FaceCube(KFaceCube):
    def is_solved(self):
        return self.f == ([0]*9 + [1]*9 + [2]*9 + [3]*9 + [4]*9 + [5]*9)

    def get_representation_strings(self):
        s = self.to_String()
        return [s[i:i + 9] for i in range(0, 6*9, 9)]
