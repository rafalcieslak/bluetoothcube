import kivy

from kociemba.pykociemba.color import color_keys

from bluetoothcube.cubestate import CubieCube, MOVES_GIIKER_TO_KOCIEMBA

from typing import List


class Move:
    def __init__(self, face: str, dir: str, count: int = 1) -> None:
        self.face = face
        self.dir = dir
        self.count = count

    def __repr__(self):
        # Internal, actual representation of the move.
        return (f"{self.face}{self.dir}"
                f"{self.count if self.count > 1 else ''}")

    def nice_str(self):
        # Nice representation, preferred by humans (no R'3 etc.)
        if not self.is_printable():
            return ""
        count = self.count % 4
        dir = self.dir
        if count == 2:
            dir = ''
        elif count == 3:
            # Inverse direction
            dir = "" if dir else "'"
            count = 1
        return (f"{self.face}{dir}{count if count > 1 else ''}")

    def is_printable(self):
        return self.count % 4 != 0

    @staticmethod
    def list_to_str(list: List['Move']):
        return ' '.join(str(m) for m in list if m.is_printable())


def merge_moves(a: Move, b: Move) -> List[Move]:
    if a.face != b.face:
        return [a, b]

    if a.dir != b.dir:
        return [a, b]

    new_count = a.count + b.count

    return [Move(a.face, a.dir, new_count)]


class BluetoothCube(kivy.event.EventDispatcher):
    solved = kivy.properties.BooleanProperty(False)

    def __init__(self):
        self.register_event_type('on_state_changed')
        self.register_event_type('on_move_raw')
        self.register_event_type('on_move_merged')
        super(BluetoothCube, self).__init__()
        self.cube_state = CubieCube()
        self.move_history_raw: List[Move] = []
        self.move_history_merged: List[Move] = []
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
        self.cube_state = CubieCube(giiker_state=state)
        self.solved = self.cube_state.is_solved()

        face = color_keys[MOVES_GIIKER_TO_KOCIEMBA[(state[16] >> 4) & 0x0F]]
        dir = ("" if (state[16] & 0x0F) == 1 else "'")
        move = Move(face, dir)
        self.move_history_raw.append(move)

        s = '  '.join(self.cube_state.get_representation_strings())
        print(f"{s}  {move}")

        self.dispatch('on_state_changed', self.cube_state)
        self.dispatch('on_move_raw', move)

        self.add_move_to_rich_history(move)

    def add_move_to_rich_history(self, move: Move):
        if len(self.move_history_merged) < 1:
            self.move_history_merged.append(move)
            return

        # Merge last two moves, if applicable
        last_move = self.move_history_merged[-1]
        self.move_history_merged.pop()
        new_moves = merge_moves(last_move, move)
        self.move_history_merged += new_moves

        # Trim the moves list to last 50 moves.
        self.move_history_merged = self.move_history_merged[-50:]

        print(Move.list_to_str(self.move_history_merged))

        self.dispatch('on_move_merged', new_moves[-1])

    def on_state_changed(self, *args):
        pass

    def on_move_raw(self, *args):
        pass

    def on_move_merged(self, *args):
        pass
