import kivy
from kivy.app import App

MOVES = ['none', 'blue', 'yellow', 'orange', 'white', 'red', 'green']


class CubeState:
    def __init__(self, giiker_state=None):
        self.c = tuple(range(1, 9))   # Corner permutation
        self.co = tuple([3] * 8)      # Corner orientations
        self.e = tuple(range(1, 13))  # Edge permutation
        self.eo = tuple([0] * 12)     # Edge orientations

        if giiker_state:
            s = giiker_state
            self.c = (s[0] >> 4 & 0xF, s[0] >> 0 & 0xF,
                      s[1] >> 4 & 0xF, s[1] >> 0 & 0xF,
                      s[2] >> 4 & 0xF, s[2] >> 0 & 0xF,
                      s[3] >> 4 & 0xF, s[3] >> 0 & 0xF)
            self.co = (s[4] >> 4 & 0xF, s[4] >> 0 & 0xF,
                       s[5] >> 4 & 0xF, s[5] >> 0 & 0xF,
                       s[6] >> 4 & 0xF, s[6] >> 0 & 0xF,
                       s[7] >> 4 & 0xF, s[7] >> 0 & 0xF)
            self.e = (s[8] >> 4 & 0xF, s[8] >> 0 & 0xF,
                      s[9] >> 4 & 0xF, s[9] >> 0 & 0xF,
                      s[10] >> 4 & 0xF, s[10] >> 0 & 0xF,
                      s[11] >> 4 & 0xF, s[11] >> 0 & 0xF,
                      s[12] >> 4 & 0xF, s[12] >> 0 & 0xF,
                      s[13] >> 4 & 0xF, s[13] >> 0 & 0xF)
            self.eo = (s[14] >> 7 & 1, s[14] >> 6 & 1,
                       s[14] >> 5 & 1, s[14] >> 4 & 1,
                       s[14] >> 3 & 1, s[14] >> 2 & 1,
                       s[14] >> 1 & 1, s[14] >> 0 & 1,
                       s[15] >> 7 & 1, s[15] >> 6 & 1,
                       s[15] >> 5 & 1, s[15] >> 4 & 1)

    def __eq__(self, other):
        return (self.c == other.c and self.co == other.co and
                self.e == other.e and self.eo == other.eo)

    def is_solved(self):
        return (self.c == tuple(range(1, 9)) and
                self.co == tuple([3] * 8) and
                self.e == tuple(range(1, 13)) and
                self.eo == tuple([0] * 12))

    def get_representation_strings(self):
        return (' '.join(str(c) for c in self.c),
                ' '.join(str(co) for co in self.co),
                ' '.join(str(e) for e in self.e),
                ' '.join(str(eo) for eo in self.eo), )


class BluetoothCube(kivy.event.EventDispatcher):
    solved = kivy.properties.BooleanProperty(False)

    def __init__(self):
        self.register_event_type('on_state_changed')
        super(BluetoothCube, self).__init__()
        self.cube_state = CubeState()
        self.connection = None

    def set_connection(self, connection):
        self.connection = connection
        self.cube_state = CubeState()
        self.connection.bind(on_state_updated=self.process_state_update)

    def disable_connection(self):
        self.cube_state = CubeState()
        self.connection = None
        self.solved = self.cube_state.is_solved()

    def process_state_update(self, connection, state):
        cube_state = CubeState(state)

        move1 = (MOVES[(state[16] >> 4) & 0x0F] +
                 ("" if (state[16] & 0x0F) == 1 else "'"))
        move2 = (MOVES[(state[17] >> 4) & 0x0F] +
                 ("" if (state[17] & 0x0F) == 1 else "'"))
        move3 = (MOVES[(state[18] >> 4) & 0x0F] +
                 ("" if (state[18] & 0x0F) == 1 else "'"))
        move4 = (MOVES[(state[19] >> 4) & 0x0F] +
                 ("" if (state[19] & 0x0F) == 1 else "'"))

        corner_pos, corner_ori, edge_pos, edge_ori = \
            cube_state.get_representation_strings()
        moves = f"{move4} {move3} {move2} {move1}"

        print(f"{corner_pos}  {corner_ori}  {edge_pos}  {edge_ori}  {moves}")

        self.cube_state = cube_state
        self.solved = cube_state.is_solved()
        self.dispatch('on_state_changed', self.cube_state)

    def on_state_changed(self, *args):
        pass
