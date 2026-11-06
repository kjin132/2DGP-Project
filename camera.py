"""플레이어를 따라가는 카메라. 모든 월드 오브젝트는 (월드 좌표 - 카메라 좌표)로 그린다."""
from config import SCREEN_W, SCREEN_H, ZOOM

Z = ZOOM
VIEW_W, VIEW_H = SCREEN_W / Z, SCREEN_H / Z     # 화면에 보이는 월드 크기

x = 0.0
y = 0.0
map_w = SCREEN_W
map_h = SCREEN_H


def set_bounds(w, h):
    global map_w, map_h
    map_w, map_h = w, h


def follow(tx, ty):
    """목표(플레이어)를 화면 가운데에 두되, 맵 밖은 보이지 않게 고정"""
    global x, y
    # 정수로 맞춰야 맵 조각과 가림 조각이 1px 도 어긋나지 않음
    x = int(min(max(tx - VIEW_W / 2, 0), max(0, map_w - VIEW_W)))
    y = int(min(max(ty - VIEW_H / 2, 0), max(0, map_h - VIEW_H)))


def to_screen(wx, wy):
    return (wx - x) * Z, (wy - y) * Z


def to_world(sx, sy):
    return sx / Z + x, sy / Z + y
