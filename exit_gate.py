"""스테이지 출구: 후보 몇 곳 중 한 곳만 열림. 바닥에 빛나는 고리로 표시하고, 가까이 가야 화면에 보임 (PRD 2.8.1)"""
import math
from pico2d import load_image
import game_framework
import camera

RADIUS = 70             # 이 안에 들어오면 출구에 도착


class ExitGate:
    image = None

    def __init__(self, x, y, name):
        if ExitGate.image is None:
            ExitGate.image = load_image('resources/effect/exit_ring.png')
        self.x, self.y, self.name = x, y, name
        self.t = 0.0

    @property
    def sort_y(self):
        return self.y + 200          # 바닥에 깔리므로 다른 것보다 먼저 그림

    def reached(self, who):
        return math.hypot(who.x - self.x, (who.y - self.y) * 1.6) < RADIUS

    def update(self):
        self.t += game_framework.frame_time

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y)
        Z = camera.Z
        pulse = 1 + 0.08 * math.sin(self.t * 4)
        ExitGate.image.opacify(0.65 + 0.35 * math.sin(self.t * 4))
        ExitGate.image.draw(sx, sy, 2 * RADIUS * Z * pulse, RADIUS * Z * pulse)
        ExitGate.image.opacify(1.0)
