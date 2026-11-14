import math
from pico2d import load_image
import game_framework
import game_world
import camera
import shadow
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
    icon = None            # resources/ui 의 그림 이름 (빛 있는 버전은 _glow)
    is_enemy_ui = False    # 적 UI (적 HP 바, 적 경보등)
    all = []               # 지금 스테이지의 UI 전부 (HUD·보안관·적이 함께 봄), play_mode 가 채워 줌

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.owner = 'floor'
        self.is_fake = False
        self.durability = 100
        self.claimed = False   # 한 번이라도 보안관 손에 들어왔는지 (적 UI 첫 획득 점수용)
        self.stolen_at = None  # 도둑이 훔쳐 간 시각 (되찾기 전까지)
        self.seen_on_map = False   # 쫓는 동안 미니맵을 켜 둔 적이 있는지 (흔적만으로 회수 판정)
        self.t = 0.0
        self.image = _image(self.icon)
        self.glow = _image(self.icon + '_glow')
        k = ITEM_WORLD_SIZE / max(self.image.w, self.image.h)
        self.w, self.h = self.image.w * k, self.image.h * k

    @property
    def active(self):
        return self.owner in ('player', 'pedestal')

    def update(self):
        self.t += game_framework.frame_time

    def destroy(self):
        """먹거나 던져서 부서짐: 이 스테이지에서 완전히 사라짐"""
        self.owner = 'gone'
        if self in UIItem.all:
            UIItem.all.remove(self)
        try:
            game_world.remove_object(self)
        except ValueError:
            pass

    def draw_at(self, sx, sy, glow=True, ground=True):
        """화면 좌표 (sx, sy) 를 바닥점으로 해서 그림. 빛은 은은하게 깜빡임.
        ground=False 면 그림자 없이 (적이 머리 위에 들고 있을 때)"""
        Z = camera.Z
        bob = math.sin(self.t * 3) * 3
        w, h = self.w * Z, self.h * Z
        cy = sy + h / 2 + (6 + bob) * Z
        if ground:
            shadow.draw(sx, sy, w * (0.75 - bob * 0.02))     # 떠 있을수록 그림자가 작아짐
        if glow:
            self.glow.opacify(0.55 + 0.45 * math.sin(self.t * 4))
            self.glow.draw(sx, cy, w, h)
            self.glow.opacify(1.0)
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


class EnemyHPItem(UIItem):
    """적 HP 바: 켜 두면 모든 적 머리 위에 남은 체력이 보임 (PRD 2.6)"""
    kind, name, icon = 'enemy_hp', '적 HP 바', 'item_enemy_hp_frame'
    is_enemy_ui = True


class EnemyAlarmItem(UIItem):
    """적 경보등: 켜 두면 갱단원이 칼을 들어 올릴 때 머리 위에 경보가 뜸 (PRD 2.6)"""
    kind, name, icon = 'enemy_alarm', '적 경보등', 'item_enemy_alarm'
    is_enemy_ui = True


ITEM_CLASSES = {c.kind: c for c in (HPBarItem, MinimapItem, CrosshairItem, AmmoGaugeItem, ScoreBoardItem,
                                    EnemyHPItem, EnemyAlarmItem)}
