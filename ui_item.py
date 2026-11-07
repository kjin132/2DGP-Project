from pico2d import load_image
import camera
from config import ITEM_WORLD_SIZE

_images = {}


def _image(name):
    if name not in _images:
        _images[name] = load_image(f'resources/ui/{name}.png')
    return _images[name]


class UIItem:
    """월드 안에 물건으로 존재하는 UI.
    owner: 'floor'(바닥) / 'player'(손에 듦) / 'pedestal'(거치대) / 'enemy'(적이 가짐)
    손에 들거나 거치대에 있을 때만 켜진 것(active)으로 보고, HUD 가 그 정보만 그린다."""
    kind = 'base'
    name = 'UI'
    icon = None            # resources/ui 의 그림 이름

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.owner = 'floor'
        self.is_fake = False
        self.durability = 100
        self.image = _image(self.icon)
        k = ITEM_WORLD_SIZE / max(self.image.w, self.image.h)
        self.w, self.h = self.image.w * k, self.image.h * k

    @property
    def active(self):
        return self.owner in ('player', 'pedestal')

    def update(self):
        pass

    def draw_at(self, sx, sy):
        """화면 좌표 (sx, sy) 를 바닥점으로 해서 그림"""
        Z = camera.Z
        w, h = self.w * Z, self.h * Z
        cy = sy + h / 2
        self.image.draw(sx, cy, w, h)

    def draw(self):
        if self.owner == 'floor':
            self.draw_at(*camera.to_screen(self.x, self.y))


class HPBarItem(UIItem):
    kind, name, icon = 'hp', 'HP 바', 'item_hp_frame'


class MinimapItem(UIItem):
    kind, name, icon = 'minimap', '미니맵', 'item_minimap'


class CrosshairItem(UIItem):
    kind, name, icon = 'crosshair', '조준선', 'item_crosshair'


class AmmoGaugeItem(UIItem):
    kind, name, icon = 'ammo', '탄약 게이지', 'item_ammo_frame'


class ScoreBoardItem(UIItem):
    kind, name, icon = 'score', '점수판', 'item_score_frame'


ITEM_CLASSES = {c.kind: c for c in (HPBarItem, MinimapItem, CrosshairItem, AmmoGaugeItem, ScoreBoardItem)}
