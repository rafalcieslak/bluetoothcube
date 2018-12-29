import kivy

from bluetoothcube.cubestate import CubieCube


MOVES = ['none', 'blue', 'yellow', 'orange', 'white', 'red', 'green']


class BluetoothCube(kivy.event.EventDispatcher):
    solved = kivy.properties.BooleanProperty(False)

    def __init__(self):
        self.register_event_type('on_state_changed')
        super(BluetoothCube, self).__init__()
        self.cube_state = CubieCube()
        self.connection = None

    def set_connection(self, connection):
        self.connection = connection
        self.cube_state = CubieCube()
        self.connection.bind(on_state_updated=self.process_state_update)

    def disable_connection(self):
        self.cube_state = CubieCube()
        self.connection = None
        self.solved = self.cube_state.is_solved()
        self.dispatch('on_state_changed', self.cube_state)

    def process_state_update(self, connection, state):
        cube_state = CubieCube(giiker_state=state)

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
