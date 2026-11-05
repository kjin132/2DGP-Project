import json
from pico2d import load_image
import camera


class Background:
    """스테이지 맵 그림 한 장 (건물·소품 포함). 너무 커서 2x2 조각으로 나눠 불러오고,
    카메라가 보는 부분만 잘라 그린다."""

    def __init__(self, folder):
        info = json.load(open(f'{folder}/map.json'))
        self.pixel_w, self.pixel_h = info['w'], info['h']
        self.cw, self.ch = info['chunk_w'], info['chunk_h']
        self.chunks = {}
        for i in range(info['cols']):
            for j in range(info['rows']):
                # 파일 이름 ground_열_행 : 행 0 이 맵 아래쪽
                self.chunks[(i, j)] = load_image(f'{folder}/ground_{i}_{j}.png')

    def update(self):
        pass

    def draw(self):
        Z = camera.Z
        l, b = camera.x, camera.y
        r, t = l + camera.VIEW_W + 1, b + camera.VIEW_H + 1
        for (i, j), img in self.chunks.items():
            x0 = i * self.cw
            y0 = img_bottom(self, j)     # 맨 아래 행 조각은 높이가 다를 수 있어 실제 높이로 계산
            cl, cb = max(l, x0), max(b, y0)
            cr, ct = min(r, x0 + img.w), min(t, y0 + img.h)
            if cr <= cl or ct <= cb:
                continue
            sl, sb = int(cl - x0), int(cb - y0)
            w, h = int(cr - cl), int(ct - cb)
            img.clip_draw_to_origin(sl, sb, w, h, (cl - l) * Z, (cb - b) * Z, w * Z, h * Z)


def img_bottom(bg, j):
    """j 번째 행(아래에서부터) 조각의 바닥 y"""
    return sum(bg.chunks[(0, k)].h for k in range(j))
