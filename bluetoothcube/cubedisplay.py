import kivy

from kivy.app import App
from kivy.vector import Vector
from kivy.uix.widget import Widget
from kivy.clock import Clock

from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color

from kociemba.pykociemba.facecube import FaceCube


STICKERS = {
    'green': [0.33, 0.6, 0.5],
    'red': [0, 0.6, 0.7],
    'blue': [0.66, 0.6, 0.6],
    'orange': [0.1, 0.85, 0.85],
    'white': [0, 0, 0.85],
    'yellow': [0.16, 0.8, 0.8]
}

# TODO: This might be user-configurable.
STICKER_COLOR = {
    0: 'white', 3: 'yellow',
    1: 'red', 4: 'orange',
    2: 'green', 5: 'blue',
}


class CubeDisplay(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.face_state = FaceCube()
        self.update_canvas()

        self.bind(pos=self.update_rect,
                  size=self.update_rect)

        self.update_canvas_trigger = Clock.create_trigger(
            lambda td: self.update_canvas())

        App.get_running_app().cube.bind(
            on_state_changed=self.on_cube_state_changed)

    def update_rect(self, *args):
        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()

        # TODO: Maybe it's possible to recompute all coordinates without
        # recreating the canvas. It may be a very complex task, though.

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

            def draw_face(o, n):
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 0]]])
                Rectangle(pos=o+(sticker_v*(0, 2)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 1]]])
                Rectangle(pos=o+(sticker_v*(1, 2)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 2]]])
                Rectangle(pos=o+(sticker_v*(2, 2)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 3]]])
                Rectangle(pos=o+(sticker_v*(0, 1)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 4]]])
                Rectangle(pos=o+(sticker_v*(1, 1)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 5]]])
                Rectangle(pos=o+(sticker_v*(2, 1)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 6]]])
                Rectangle(pos=o+(sticker_v*(0, 0)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 7]]])
                Rectangle(pos=o+(sticker_v*(1, 0)), size=sticker_v)
                Color(hsv=STICKERS[STICKER_COLOR[self.face_state.f[n + 8]]])
                Rectangle(pos=o+(sticker_v*(2, 0)), size=sticker_v)

            draw_face(face(1, 2), 0 * 9)  # U
            draw_face(face(2, 1), 1 * 9)  # R
            draw_face(face(1, 1), 2 * 9)  # F
            draw_face(face(1, 0), 3 * 9)  # D
            draw_face(face(0, 1), 4 * 9)  # L
            draw_face(face(3, 1), 5 * 9)  # B

    def on_cube_state_changed(self, cube, newstate):
        self.face_state = newstate.toFaceCube()
        self.update_canvas_trigger()
