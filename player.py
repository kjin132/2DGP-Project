import game_framework
import camera
import sheriff_sprites
from config import CHAR_SCALE


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.sprites = sheriff_sprites.load()
        self.t = 0.0                  # 현재 애니메이션 재생 시간

    def handle_event(self, e):
        pass

    def update(self):
        self.t += game_framework.frame_time

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y)
        sheet = self.sprites['idle_front']
        sheet.draw(sheet.frame_at(self.t), sx, sy, CHAR_SCALE * camera.Z)
