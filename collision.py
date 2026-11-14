"""맵 충돌 (resources/map/stage1/collision.png 를 읽어 4px 칸 격자로 만듦)

collision.png 는 맵 그림과 같은 크기(5120 x 2860)의 그림이고, 색으로 충돌을 정한다.
  빨강 (투명하지 않고 빨강이 파랑보다 진함) : 막힘 — 사람·총알 모두 막힘 (집, 울타리, 큰 바위, 절벽)
  파랑 (투명하지 않고 파랑이 빨강보다 진함) : 물 — 사람만 막힘, 총알은 지나감
  투명                                     : 걸을 수 있음
그림 편집 프로그램에서 맵 그림을 아래 레이어로 깔고 칠하면 된다.
4px 칸마다 가운데 픽셀 하나로 판정하므로 4px 보다 가는 선은 무시될 수 있다.
"""
import ctypes
import json
import sdl2
import sdl2.sdlimage

WALK, SOLID, WATER = 0, 1, 2


def _read_png(path):
    """PNG 를 RGBA 바이트로 읽음 (pico2d 가 쓰는 SDL 로 읽어서 따로 설치할 것이 없음)"""
    surf = sdl2.sdlimage.IMG_Load(path.encode('utf-8'))
    if not surf:
        raise FileNotFoundError(path)
    rgba = sdl2.SDL_ConvertSurfaceFormat(surf, sdl2.SDL_PIXELFORMAT_ABGR8888, 0)   # 메모리 순서 R, G, B, A
    sdl2.SDL_FreeSurface(surf)
    s = rgba.contents
    w, h, pitch = s.w, s.h, s.pitch
    data = ctypes.string_at(s.pixels, pitch * h)
    sdl2.SDL_FreeSurface(rgba)
    return w, h, pitch, data


class CollisionMap:
    def __init__(self, folder):
        info = json.load(open(f'{folder}/map.json'))
        self.cell = c = info['grid']
        w, h, pitch, px = _read_png(f'{folder}/collision.png')
        self.gw, self.gh = w // c, h // c
        rows = []
        # 게임 좌표는 아래가 0 이므로 그림의 아래쪽 줄부터 읽음
        for gy in range(self.gh):
            y = h - 1 - (gy * c + c // 2)
            row = px[y * pitch:(y + 1) * pitch]
            off = (c // 2) * 4                   # 칸 가운데 픽셀
            step = c * 4
            r = row[off::step][:self.gw]
            b = row[off + 2::step][:self.gw]
            a = row[off + 3::step][:self.gw]
            rows.append(bytes(WALK if aa < 128 else (WATER if bb > rr else SOLID)
                              for rr, bb, aa in zip(r, b, a)))
        self.data = b''.join(rows)

    def at(self, x, y):
        cx, cy = int(x // self.cell), int(y // self.cell)
        if cx < 0 or cy < 0 or cx >= self.gw or cy >= self.gh:
            return SOLID                      # 맵 밖은 막힘
        return self.data[cy * self.gw + cx]

    def blocks_walk(self, l, b, r, t):
        """사각형(몸 충돌 상자) 안에 막힌 칸이 하나라도 있는지"""
        c = self.cell
        for cy in range(int(b // c), int(t // c) + 1):
            for cx in range(int(l // c), int(r // c) + 1):
                if self.at(cx * c + 1, cy * c + 1) != WALK:
                    return True
        return False

    def blocks_bullet(self, x, y):
        return self.at(x, y) == SOLID

    def line_clear(self, x0, y0, x1, y1):
        """두 점 사이에 건물·울타리·절벽이 없으면 True (물은 시야를 가리지 않음).
        한 칸(4px)씩 따라가며 검사한다."""
        d = max(abs(x1 - x0), abs(y1 - y0))
        n = max(1, int(d // self.cell))
        for i in range(1, n):
            t = i / n
            if self.at(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) == SOLID:
                return False
        return True


def overlaps(a, b):
    """두 사각형 (left, bottom, right, top) 이 겹치는지"""
    al, ab, ar, at = a
    bl, bb, br, bt = b
    return al < br and bl < ar and ab < bt and bb < at
