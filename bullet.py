import math
from pico2d import load_image
import game_framework
import game_world
import camera
from config import BULLET_SPEED, BULLET_LIFE, BULLET_SIZE


class Bullet:
    image = None

    def __init__(self, x, y, angle):
        if Bullet.image is None:
            Bullet.image = load_image('resources/effect/bullet.png')   # 탄두가 위를 보는 그림
        self.x, self.y = x, y          # y 는 그림 위치(총구 높이)
        self.angle = angle
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.life = BULLET_LIFE

    def update(self):
        dt = game_framework.frame_time
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            game_world.remove_object(self)

    def draw(self):
        # 그림이 위(+90도)를 보고 있으므로 90도 빼서 날아가는 방향을 보게 함
        sx, sy = camera.to_screen(self.x, self.y)
        Bullet.image.composite_draw(self.angle - math.pi / 2, '', sx, sy,
                                    BULLET_SIZE[0] * camera.Z, BULLET_SIZE[1] * camera.Z)
