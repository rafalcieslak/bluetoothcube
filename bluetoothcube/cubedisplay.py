import kivy

from kivy.vector import Vector
from kivy.uix.widget import Widget

from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color

STICKERS = {
    'green': [0.33, 0.6, 0.5],
    'red': [0, 0.6, 0.7],
    'blue': [0.66, 0.6, 0.6],
    'orange': [0.1, 0.85, 0.85],
    'white': [0, 0, 0.85],
    'yellow': [0.16, 0.8, 0.8]}


class CubeDisplay(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_canvas()

        self.bind(pos=self.update_rect,
                  size=self.update_rect)

    def update_rect(self, *args):
        # TODO: Maybe it's possible to recompute all coordinates without
        # recreating the canvas. It may be a very complex task, though.
        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            pos = Vector(self.pos[:2])
            if self.width * 3 > self.height * 4:
                # Fill to height
                area_size = Vector(4*self.height/3, self.height)
                origin = pos + Vector((self.width - area_size[0])/2, 0)
            else:
                # Fill to width
                area_size = Vector(self.width, 3*self.width/4)
                origin = pos + Vector(0, (self.height - area_size[1])/2)

            sticker_v = area_size / Vector(12, 9)
            face_v = area_size / Vector(4, 3)

            def face(x, y):
                return origin + face_v * (x, y)

            # F-face
            Color(hsv=STICKERS['green'])
            Rectangle(pos=face(1, 0), size=face_v)

            # U-face
            Color(hsv=STICKERS['white'])
            Rectangle(pos=face(1, 1), size=face_v)

            # L-face
            Color(hsv=STICKERS['orange'])
            Rectangle(pos=face(0, 1), size=face_v)

            # B-face
            Color(hsv=STICKERS['blue'])
            Rectangle(pos=face(1, 2), size=face_v)

            # L-face
            Color(hsv=STICKERS['red'])
            Rectangle(pos=face(2, 1), size=face_v)

            # D-face
            Color(hsv=STICKERS['yellow'])
            Rectangle(pos=face(3, 1), size=face_v)

    def apply_cube_state(self, newstate):
        pass
