import kociemba.pykociemba as kociemba
from kociemba.pykociemba.cubiecube import CubieCube as KCubieCube
from kociemba.pykociemba.facecube import FaceCube as KFaceCube

from typing import List

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


# Translates Giiker move IDs to pykociemba
MOVES_GIIKER_TO_KOCIEMBA = [None, 5, 3, 4, 0, 1, 2]


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

    def toFaceCube(self):
        facecube = super().toFaceCube()
        # Return our custom facecube subclass
        return FaceCube(facecube.f)


class FaceCube(KFaceCube):
    SOLVED_PATTERN = "U"*9 + "L"*9 + "F"*9 + "R"*9 + "B"*9 + "D"*9

    PRETTY_PATTERN = """\
      U U U
      U U U
      U U U
L L L F F F R R R B B B
L L L F F F R R R B B B
L L L F F F R R R B B B
      D D D
      D D D
      D D D\
"""
    ROT_CLOCKWISE = [6, 3, 0, 7, 4, 1, 8, 5, 2]
    ROT_ACLOCKWISE = [2, 5, 8, 1, 4, 7, 0, 3, 6]
    ROTATIONS = {
        "x":  {'R': '+', 'L': '-', 'U': 'F', 'B': 'U++', 'D': 'B++', 'F': 'D'},
        "x'": {'R': '-', 'L': '+', 'U': 'B++', 'B': 'D++', 'D': 'F', 'F': 'U'},
        "y": {'U': '+', 'D': '-', 'L': 'F', 'F': 'R', 'R': 'B', 'B': 'L'},
        "y'": {'U': '-', 'D': '+', 'L': 'B', 'F': 'L', 'R': 'F', 'B': 'R'},
        "z": {'F': '+', 'B': '-', 'R': 'U+', 'U': 'L+', 'L': 'D+', 'D': 'R+'},
        "z'": {'F': '-', 'B': '+', 'R': 'D-', 'U': 'R-', 'L': 'U-', 'D': 'L-'},
    }

    def __init__(self, data=None):
        # This custom constructor additionally accepts a list of colors.
        if not data:
            super().__init__()
        elif isinstance(data, str):
            super().__init__(data)
        elif isinstance(data, list):
            x = data[0]
            if isinstance(x, str):
                self.f = [kociemba.color.colors.get(i, -1) for i in data]
            else:
                self.f = data
        else:
            raise NotImplementedError()

    def is_solved(self):
        return self.f == ([0]*9 + [1]*9 + [2]*9 + [3]*9 + [4]*9 + [5]*9)

    def get_representation_strings(self):
        s = self.to_String()
        return [s[i:i + 9] for i in range(0, 6*9, 9)]

    def get_face(self, f):
        i = kociemba.color.colors[f] * 9
        return self.f[i:i+9]

    # TODO: This method deserves some unit-tests.
    def rotated(self, r: str, normalize_colors=True) -> 'FaceCube':
        # TODO: Accept compound rotations, like zx'y.

        faces = {f: self.get_face(f) for f in "URFDLB"}
        rotation = self.ROTATIONS[r]

        def process_face(face, rules):
            for rule in rules:
                if rule in "URFDLB":
                    face = faces[rule]
                elif rule == '+':
                    face = [face[self.ROT_CLOCKWISE[i]] for i in range(0, 9)]
                elif rule == '-':
                    face = [face[self.ROT_ACLOCKWISE[i]] for i in range(0, 9)]
                else:
                    raise ValueError("Invalid face rule: {rule}")
            return face

        new_faces = sum(
            (process_face(faces[f], rotation[f]) for f in "URFDLB"),
            [])

        if normalize_colors:
            # Rename colors so that U center is at U face etc.
            color_map = {new_faces[f*9 + 4]: f for f in range(0, 6)}
            new_faces = [color_map[i] if i >= 0 else i for i in new_faces]

        return FaceCube(new_faces)

    def pretty_str(self) -> str:
        faces = {f: self.get_face(f) for f in "URFDLB"}
        res = ""
        for ch in self.PRETTY_PATTERN:
            if ch not in "URFDLB":
                res += ch
                continue
            i = faces[ch][0]
            if i == -1:
                res += "."
            else:
                res += kociemba.color.color_keys[i]
            faces[ch] = faces[ch][1:]
        return res

    def matches_any(self, patterns: List['FaceCube']) -> bool:
        for pattern in patterns:
            if self.matches(pattern):
                return True
        return False

    def matches(self, pattern: 'FaceCube') -> bool:
        for x, p in zip(self.f, pattern.f):
            if p != -1 and x != p:
                return False
        return True
