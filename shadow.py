"""발밑 그림자: 반투명 타원을 본체보다 먼저 그린다"""
from pico2d import load_image

_image = None
ALPHA = 0.7


def draw(sx, sy, w, h=None):
    global _image
    if _image is None:
        _image = load_image('resources/effect/shadow.png')
        _image.opacify(ALPHA)
    _image.draw(sx, sy, w, h if h is not None else w * 0.32)
