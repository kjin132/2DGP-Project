import math
from pico2d import *
import game_framework
import camera
import sheriff_sprites
import shadow
from config import CHAR_SCALE, PLAYER_SPEED, DASH_TIME, DASH_SPEED

MOVE_KEYS = {SDLK_w: (0, 1), SDLK_s: (0, -1), SDLK_a: (-1, 0), SDLK_d: (1, 0)}

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.sprites = sheriff_sprites.load()
        self.held = set()             # 눌려 있는 이동 키
        self.facing = 'down'          # down / up / left / right
        self.state = 'idle'           # idle / walk / dash
        self.t = 0.0                  # 현재 애니메이션 재생 시간
        self.dash_dir = (1, 0)

    # ---------- 입력 ----------
    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key in MOVE_KEYS:
            self.held.add(e.key)
        elif e.type == SDL_KEYUP and e.key in MOVE_KEYS:
            self.held.discard(e.key)
        elif e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            self.start_dash()


    def start_dash(self):
        if self.state == 'dash':
            return
        dx, dy = self.move_dir()
        if not (dx or dy):
            return
        n = math.hypot(dx, dy)
        self.dash_dir = (dx / n, dy / n)
        if dx:
            self.facing = 'right' if dx > 0 else 'left'
        self.set_state('dash')

    def move_dir(self):
        dx = sum(MOVE_KEYS[k][0] for k in self.held)
        dy = sum(MOVE_KEYS[k][1] for k in self.held)
        return dx, dy

    def set_state(self, s):
        if s != self.state:
            self.state = s
            self.t = 0.0

    # ---------- 갱신 ----------
    def update(self):
        dt = game_framework.frame_time
        self.t += dt
        if self.state == 'dash':
            self.try_move(self.dash_dir[0] * PLAYER_SPEED * DASH_SPEED * dt,
                          self.dash_dir[1] * PLAYER_SPEED * DASH_SPEED * dt)
            self.clamp_to_map()
            if self.t >= DASH_TIME:
                self.set_state('idle')
            return
        dx, dy = self.move_dir()
        if dx or dy:
            n = math.hypot(dx, dy)
            self.try_move(dx / n * PLAYER_SPEED * dt, dy / n * PLAYER_SPEED * dt)
            self.clamp_to_map()
            if dx:
                self.facing = 'right' if dx > 0 else 'left'
            else:
                self.facing = 'up' if dy > 0 else 'down'
            self.set_state('walk')
        else:
            self.set_state('idle')

    # ---------- 그리기 ----------
    def view(self):
        """facing 에 맞는 시트 접미사와 좌우 반전 여부"""
        if self.facing == 'up':
            return 'back', False
        if self.facing == 'down':
            return 'front', False
        return 'side', self.facing == 'left'

    collision = None    # 맵 충돌 격자, play_mode 가 채워 줌

    def foot_bb(self, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        return x - 12, y, x + 12, y + 10

    def blocked(self, x, y):
        return Player.collision is not None and Player.collision.blocks_walk(*self.foot_bb(x, y))

    def try_move(self, dx, dy):
        """x, y 를 따로 움직여 보고 막히면 그 축만 취소 (벽을 따라 미끄러지듯)"""
        if dx and not self.blocked(self.x + dx, self.y):
            self.x += dx
        if dy and not self.blocked(self.x, self.y + dy):
            self.y += dy

    def clamp_to_map(self):
        self.x = min(max(self.x, 20), camera.map_w - 20)
        self.y = min(max(self.y, 10), camera.map_h - 60)

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y)
        shadow.draw(sx, sy + 2, 46 * camera.Z)
        scale = CHAR_SCALE * camera.Z
        suffix, flip = self.view()
        if self.state == 'dash':                     # 대시는 일단 걷기 그림으로
            sheet = self.sprites[f'walk_{suffix}']
            sheet.draw(sheet.frame_at(self.t * 2), sx, sy, scale, flip)
            return
        sheet = self.sprites[f'{self.state}_{suffix}']
        sheet.draw(sheet.frame_at(self.t), sx, sy, scale, flip)
