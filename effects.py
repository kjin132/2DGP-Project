"""잠깐 보였다 사라지는 효과들"""
import math
import random
import game_framework
import game_world
import camera
from config import ITEM_WORLD_SIZE


class Shards:
    """UI 가 부서질 때: UI 그림을 작은 조각으로 잘라 사방으로 흩뿌림"""
    LIFE = 0.7
    GRAVITY = 700

    def __init__(self, image, x, y, height=40, n=16):
        self.image = image
        self.x, self.y = x, y
        self.t = 0.0
        self.k = ITEM_WORLD_SIZE / max(image.w, image.h)      # 그림 1px → 월드 몇 px
        pw, ph = max(1, image.w // 5), max(1, image.h // 5)
        self.parts = []
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(60, 190)
            self.parts.append({
                'src': (random.randint(0, image.w - pw), random.randint(0, image.h - ph), pw, ph),
                'x': 0.0, 'y': 0.0, 'z': float(height),             # z: 바닥에서 높이
                'vx': math.cos(a) * v, 'vy': math.sin(a) * v * 0.5, 'vz': random.uniform(80, 220),
            })

    @property
    def sort_y(self):
        return self.y - 1

    def update(self):
        dt = game_framework.frame_time
        self.t += dt
        for p in self.parts:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vz'] -= self.GRAVITY * dt
            p['z'] = max(0.0, p['z'] + p['vz'] * dt)
        if self.t >= self.LIFE:
            game_world.remove_object(self)

    def draw(self):
        Z = camera.Z
        self.image.opacify(max(0.0, 1 - self.t / self.LIFE))
        for p in self.parts:
            sx, sy, pw, ph = p['src']
            cx, cy = camera.to_screen(self.x + p['x'], self.y + p['y'] + p['z'])
            self.image.clip_draw(sx, sy, pw, ph, cx, cy, pw * self.k * Z, ph * self.k * Z)
        self.image.opacify(1.0)
