"""건물·소품의 윗부분을 캐릭터 위에 다시 그리는 조각들
맵 그림을 높이 띠로 나눠 둔 조각마다 '바닥에 닿는 높이(sort_y)'가 있어서,
캐릭터가 그보다 뒤(위쪽)에 있으면 조각이 캐릭터를 가린다."""
import json
from pico2d import load_image
import camera

BUCKET = 256        # 화면에 보이는 조각만 빨리 찾으려고 칸으로 나눠 둠


class Piece:
    __slots__ = ('atlas', 'ax', 'ay', 'w', 'h', 'x', 'y', 'sort_y')

    def __init__(self, atlas, m):
        _, self.ax, self.ay, self.w, self.h, self.x, self.y, self.sort_y = m
        self.atlas = atlas

    def update(self):
        pass

    def draw(self):
        Z = camera.Z
        sx, sy = camera.to_screen(self.x, self.y)
        self.atlas.clip_draw_to_origin(self.ax, self.ay, self.w, self.h, sx, sy, self.w * Z, self.h * Z)


class OverlaySet:
    def __init__(self, folder):
        meta = json.load(open(f'{folder}/overlay.json'))
        n = max(m[0] for m in meta) + 1
        atlases = [load_image(f'{folder}/overlay_{i}.png') for i in range(n)]
        self.buckets = {}
        for m in meta:
            p = Piece(atlases[m[0]], m)
            for bx in range(p.x // BUCKET, (p.x + p.w) // BUCKET + 1):
                for by in range(p.y // BUCKET, (p.y + p.h) // BUCKET + 1):
                    self.buckets.setdefault((bx, by), []).append(p)

    def visible(self):
        l, b = camera.x, camera.y
        r, t = l + camera.VIEW_W, b + camera.VIEW_H
        seen = set()
        out = []
        for bx in range(int(l // BUCKET), int(r // BUCKET) + 1):
            for by in range(int(b // BUCKET), int(t // BUCKET) + 1):
                for p in self.buckets.get((bx, by), ()):
                    if id(p) in seen:
                        continue
                    seen.add(id(p))
                    if p.x < r and p.x + p.w > l and p.y < t and p.y + p.h > b:
                        out.append(p)
        return out
