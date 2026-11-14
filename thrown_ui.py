"""Q 로 던진 UI: 마우스 쪽으로 날아가 적에게 맞으면 큰 피해. 맞든 안 맞든 부서져 사라짐 (PRD 2.1, 3.4)"""
import math
import game_framework
import game_world
import camera
from config import THROW_SPEED, THROW_RANGE, THROW_DAMAGE


class ThrownUI:
    collision = None    # 맵 충돌 격자
    targets = []        # 맞을 수 있는 적 목록

    def __init__(self, item, x, y, tx, ty):
        self.item = item
        self.x, self.y = x, y                  # 바닥 기준 위치
        self.height = 50                       # 손 높이에서 날아감
        d = math.hypot(tx - x, ty - y) or 1
        self.vx, self.vy = (tx - x) / d * THROW_SPEED, (ty - y) / d * THROW_SPEED
        self.dist = 0.0
        self.spin = 0.0

    @property
    def sort_y(self):
        return self.y

    def update(self):
        dt = game_framework.frame_time
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.dist += THROW_SPEED * dt
        self.spin += 12 * dt
        hit = None
        for e in ThrownUI.targets:
            if e.alive and e.hit_by_point(self.x, self.y + self.height):
                hit = e
                break
        if hit:
            hit.take_hit(THROW_DAMAGE)
        wall = ThrownUI.collision is not None and ThrownUI.collision.blocks_bullet(self.x, self.y)
        if hit or wall or self.dist >= THROW_RANGE:
            self.shatter()

    def shatter(self):
        game_world.remove_object(self)

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y + self.height)
        img = self.item.image
        w, h = self.item.w * camera.Z, self.item.h * camera.Z
        img.composite_draw(self.spin, '', sx, sy, w, h)
