import math
from pico2d import *
import game_framework
import game_world
import camera
import sheriff_sprites
import shadow
from bullet import Bullet
from config import (CHAR_SCALE, PLAYER_SPEED, DASH_TIME, DASH_SPEED, DASH_COOLDOWN,
                    MAX_AMMO, RELOAD_TIME, FIRE_INTERVAL, PICK_RANGE)

GUN_HEIGHT = 56        # 발에서 총구까지 높이 (화면 px)
GUN_REACH = 38         # 몸 중심에서 총구까지 가로 거리

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
        self.dash_cool = 0.0
        self.invincible = False
        self.aim_x, self.aim_y = x + 100, y       # 마우스가 가리키는 월드 좌표
        self.ammo = MAX_AMMO
        self.reload_t = 0.0                       # 0 보다 크면 재장전 중
        self.fire_cool = 0.0
        self.hands = [None, None]                 # 손 슬롯 2칸
        self.selected = 0                         # 1/2 키로 고른 슬롯

    # ---------- 입력 ----------
    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key in MOVE_KEYS:
            self.held.add(e.key)
        elif e.type == SDL_KEYUP and e.key in MOVE_KEYS:
            self.held.discard(e.key)
        elif e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            self.start_dash()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_r:
            self.start_reload()
        elif e.type == SDL_KEYDOWN and e.key in (SDLK_1, SDLK_2):
            self.selected = 0 if e.key == SDLK_1 else 1
        elif e.type == SDL_KEYDOWN and e.key == SDLK_e:
            self.interact()

    # ---------- UI 줍기 / 내려놓기 ----------
    items = []          # 맵의 UI 목록, play_mode 가 채워 줌
    pedestals = []      # 거치대 목록

    def nearest(self, objs, cond):
        best, bd = None, PICK_RANGE
        for o in objs:
            if cond(o):
                d = math.hypot(o.x - self.x, o.y - self.y)
                if d < bd:
                    best, bd = o, d
        return best

    def interaction_target(self):
        """E 키를 누르면 할 일과 대상 (PRD 2.1 판정 순서)
        1 바닥 UI 줍기 → 2 내려놓기"""
        item = self.nearest(Player.items, lambda o: o.owner == 'floor')
        if item:
            return 'pickup', item
        if self.hands[self.selected]:
            return 'drop', None
        return None, None

    def interact(self):
        if self.state == 'dash':
            return
        action, target = self.interaction_target()
        if action == 'pickup':
            self.pick_up(target)
        elif action == 'drop':
            self.put_down(self.hands[self.selected], self.x, self.y)
            self.hands[self.selected] = None

    def pick_up(self, item):
        """빈 슬롯에 넣음. 손이 꽉 차 있으면 선택한 슬롯의 UI 와 바꾸고, 들고 있던 것은 그 자리에 떨어뜨림"""
        if self.hands[self.selected] is None:
            slot = self.selected
        elif None in self.hands:
            slot = self.hands.index(None)
        else:
            slot = self.selected
            self.put_down(self.hands[slot], item.x, item.y)
        item.owner = 'player'
        self.hands[slot] = item

    def put_down(self, item, x, y):
        item.owner = 'floor'
        item.x, item.y = x, y

    def set_aim(self, wx, wy):
        self.aim_x, self.aim_y = wx, wy

    def start_reload(self):
        if self.reload_t <= 0 and self.ammo < MAX_AMMO:
            self.reload_t = RELOAD_TIME

    def fire(self):
        if self.state == 'dash' or self.reload_t > 0 or self.fire_cool > 0:
            return
        if self.ammo <= 0:
            self.start_reload()
            return
        right = self.aim_x >= self.x
        gx = self.x + (GUN_REACH if right else -GUN_REACH)
        gy = self.y + GUN_HEIGHT
        angle = math.atan2(self.aim_y - gy, self.aim_x - gx)
        game_world.add_object(Bullet(gx, gy, angle), 1)
        self.ammo -= 1
        self.fire_cool = FIRE_INTERVAL
        self.facing = 'right' if right else 'left'
        if self.state == 'idle' or self.state == 'shoot':   # 서서 쏘면 사격 동작, 걸으면서 쏘면 걷기 유지
            self.state, self.t = 'shoot', 0.0
        if self.ammo == 0:
            self.start_reload()

    def start_dash(self):
        if self.state == 'dash' or self.dash_cool > 0:
            return
        dx, dy = self.move_dir()
        if not (dx or dy):                         # 서 있으면 바라보는 쪽으로
            dx, dy = {'right': (1, 0), 'left': (-1, 0), 'up': (0, 1), 'down': (0, -1)}[self.facing]
        n = math.hypot(dx, dy)
        self.dash_dir = (dx / n, dy / n)
        if dx:
            self.facing = 'right' if dx > 0 else 'left'
        self.set_state('dash')
        self.invincible = True

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
        self.dash_cool = max(0.0, self.dash_cool - dt)
        self.fire_cool = max(0.0, self.fire_cool - dt)
        if self.reload_t > 0:
            self.reload_t -= dt
            if self.reload_t <= 0:
                self.ammo = MAX_AMMO
        if self.state == 'dash':
            self.try_move(self.dash_dir[0] * PLAYER_SPEED * DASH_SPEED * dt,
                          self.dash_dir[1] * PLAYER_SPEED * DASH_SPEED * dt)
            self.clamp_to_map()
            if self.t >= DASH_TIME:
                self.invincible = False
                self.dash_cool = DASH_COOLDOWN
                self.set_state('idle')
            return
        dx, dy = self.move_dir()
        if self.state == 'shoot' and not (dx or dy):
            if self.sprites['shoot'].finished(self.t * 2):
                self.set_state('idle')
            return
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
        from collision import overlaps
        bb = self.foot_bb(x, y)
        if Player.collision and Player.collision.blocks_walk(*bb):
            return True
        return any(overlaps(bb, p.get_bb()) for p in Player.pedestals)

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
        if self.state == 'dash':                     # 대시는 옆모습 한 종류
            sheet, flip = self.sprites['dash'], self.facing == 'left'
            sheet.draw(sheet.frame_at(self.t * 2), sx, sy, scale, flip)
            return
        if self.state == 'shoot':                    # 사격은 옆모습, 2배속
            sheet = self.sprites['shoot']
            sheet.draw(sheet.frame_at(self.t * 2), sx, sy, scale, self.facing == 'left')
            return
        sheet = self.sprites[f'{self.state}_{suffix}']
        sheet.draw(sheet.frame_at(self.t), sx, sy, scale, flip)
