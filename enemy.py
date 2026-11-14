"""적 공통: 맵 위를 걷고, 맞으면 느려지고, 쓰러지면 가진 UI 를 떨어뜨린다 (PRD 2.5)"""
import math
import game_framework
import camera
import shadow
import enemy_sprites
from body import Body
from config import CHAR_SCALE, PLAYER_SPEED, ENEMY_SPEED_MUL, VIEW_DIST, VIEW_ANGLE


class Enemy(Body):
    who = None              # 스프라이트 묶음 이름 ('thief' / 'grunt')
    max_hp = 30
    target = None           # 쫓을 대상(보안관), play_mode 가 채워 줌

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.sprites = enemy_sprites.load(self.who)
        self.hp = self.max_hp
        self.facing = 'down'
        self.state = 'wander'
        self.t = 0.0                  # 지금 동작의 재생 시간
        self.moving = False

    # ---------- 이동 ----------
    def speed(self):
        return PLAYER_SPEED * ENEMY_SPEED_MUL

    def face_toward(self, dx, dy):
        if abs(dx) >= abs(dy):
            self.facing = 'right' if dx > 0 else 'left'
        else:
            self.facing = 'up' if dy > 0 else 'down'

    def step_toward(self, tx, ty, dt, speed=None):
        """(tx, ty) 쪽으로 한 프레임 이동. 도착했으면 True"""
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        v = (speed or self.speed()) * dt
        if d <= max(v, 2):
            self.moving = not self.blocked(tx, ty)
            if self.moving:
                self.x, self.y = tx, ty
            return True
        self.face_toward(dx, dy)
        self.moving = self.try_move(dx / d * v, dy / d * v)
        return False

    # ---------- 시야 ----------
    FACING_DIR = {'right': (1, 0), 'left': (-1, 0), 'up': (0, 1), 'down': (0, -1)}

    def can_see(self, who):
        """앞쪽 시야(거리·각도) 안에 있고 건물에 가려지지 않으면 보임 (PRD 2.5 시야)"""
        dx, dy = who.x - self.x, who.y - self.y
        d = math.hypot(dx, dy)
        if d > VIEW_DIST:
            return False
        if d > 1:
            fx, fy = self.FACING_DIR[self.facing]
            cos = (dx * fx + dy * fy) / d
            if cos < math.cos(math.radians(VIEW_ANGLE / 2)):
                return False
        return Body.collision is None or Body.collision.line_clear(self.x, self.y + 10, who.x, who.y + 10)

    def set_state(self, s):
        if s != self.state:
            self.state = s
            self.t = 0.0

    def update(self):
        self.t += game_framework.frame_time

    # ---------- 그리기 ----------
    def sheet(self):
        """지금 그릴 시트와 좌우 반전 여부"""
        if self.facing == 'up':
            return self.sprites['walk_back'], False
        if self.facing == 'down':
            return self.sprites['walk_front'], False
        return self.sprites['walk_side'], self.facing == 'left'

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y)
        shadow.draw(sx, sy + 2, 46 * camera.Z)
        sheet, flip = self.sheet()
        frame = sheet.frame_at(self.t) if self.moving else 0     # 서 있을 때는 걷기 첫 장면
        sheet.draw(frame, sx, sy, CHAR_SCALE * camera.Z, flip)
