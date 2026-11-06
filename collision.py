"""맵 그림에서 뽑은 충돌 격자 (4px 한 칸)
0: 걸을 수 있음 / 1: 건물·소품·절벽 (사람·총알 모두 막힘) / 2: 물 (사람만 막힘)"""
import json
import zlib

WALK, SOLID, WATER = 0, 1, 2


class CollisionMap:
    def __init__(self, folder):
        info = json.load(open(f'{folder}/map.json'))
        self.cell = info['grid']
        self.gw, self.gh = info['grid_w'], info['grid_h']
        self.data = zlib.decompress(open(f'{folder}/collision.bin', 'rb').read())

    def at(self, x, y):
        cx, cy = int(x // self.cell), int(y // self.cell)
        if cx < 0 or cy < 0 or cx >= self.gw or cy >= self.gh:
            return SOLID                      # 맵 밖은 막힘
        return self.data[cy * self.gw + cx]

    def blocks_walk(self, l, b, r, t):
        """사각형(발 상자) 안에 막힌 칸이 하나라도 있는지"""
        c = self.cell
        for cy in range(int(b // c), int(t // c) + 1):
            for cx in range(int(l // c), int(r // c) + 1):
                if self.at(cx * c + 1, cy * c + 1) != WALK:
                    return True
        return False
