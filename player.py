import math
import random
from pico2d import *
import game_framework
import game_world
import camera
import sheriff_sprites
import shadow
from bullet import Bullet
from thrown_ui import ThrownUI
from body import Body
from config import (CHAR_SCALE, PLAYER_SPEED, WALK_CADENCE, DASH_TIME, DASH_SPEED, DASH_COOLDOWN,
                    MAX_AMMO, RELOAD_TIME, FIRE_INTERVAL, PICK_RANGE, MAX_HP, HURT_INVINCIBLE,
                    WEIGHT_SPEED, EAT_AMOUNT, HURT_DROP_CHANCE)

GUN_HEIGHT = 56        # 발에서 총구까지 높이 (화면 px)
GUN_REACH = 38         # 몸 중심에서 총구까지 가로 거리

MOVE_KEYS = {SDLK_w: (0, 1), SDLK_s: (0, -1), SDLK_a: (-1, 0), SDLK_d: (1, 0)}

# 제자리에서 하는 동작과 재생 배속. 이 동작들이 끝날 때까지는 걸을 수 없음 (모두 옆모습 그림)
ACTIONS = {'pickup': 1.6, 'shoot': 2.0, 'eat': 2.4, 'throw': 2.2}
EAT_FRAME = 24         # 먹기: 손이 입에 닿는 장면 (이때 UI 가 사라지고 체력이 바뀜)
THROW_FRAME = 12       # 던지기: 팔을 앞으로 뻗어 손에서 놓는 장면 (이때 UI 가 날아감)


class Player(Body):
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
        self.hp = MAX_HP
        self.hands = [None, None]                 # 손 슬롯 2칸
        self.selected = 0                         # 1/2 키로 고른 슬롯
        self.hurt_t = 0.0                         # 0 보다 크면 맞은 직후 무적
        self.walk_t = 0.0                         # 걷기 동작이 돈 횟수 (움직인 거리에 비례)
        self.using = None                         # 먹거나 던지려고 손에 쥔 UI (동작 중간에 실제로 쓰임)

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
        elif e.type == SDL_KEYDOWN and e.key == SDLK_f:
            self.eat()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_q:
            self.throw()

    # ---------- UI 줍기 / 내려놓기 ----------
    items = []          # 맵의 UI 목록, play_mode 가 채워 줌
    on_receive = None   # UI 가 손에 들어올 때마다 부를 함수, play_mode 가 채워 줌

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
        1 바닥 UI 줍기 → 2 거치대의 UI 줍기 → 3 빈 거치대에 설치 → 4 내려놓기"""
        item = self.nearest(Player.items, lambda o: o.owner == 'floor')
        if item:
            return 'pickup', item
        ped = self.nearest(Body.pedestals, lambda p: p.item is not None)
        if ped:
            return 'take', ped
        ped = self.nearest(Body.pedestals, lambda p: p.item is None)
        if ped and self.hands[self.selected]:
            return 'install', ped
        if self.hands[self.selected]:
            return 'drop', None
        return None, None

    def busy(self):
        """대시나 줍기·먹기·던지기 동작 중 (다른 손동작을 시작할 수 없음)"""
        return self.state in ('dash', 'pickup', 'eat', 'throw')

    def interact(self):
        if self.busy():
            return
        action, target = self.interaction_target()
        if action == 'pickup':
            self.pick_up(target)
        elif action == 'take':
            self.take_from(target)
        elif action == 'install':
            target.place(self.hands[self.selected])
            self.hands[self.selected] = None
        elif action == 'drop':
            self.put_down(self.hands[self.selected], self.x, self.y)
            self.hands[self.selected] = None
        if action:
            self.set_state('pickup')

    def pick_up(self, item):
        """빈 슬롯에 넣음. 손이 꽉 차 있으면 선택한 슬롯의 UI 와 바꾸고, 들고 있던 것은 그 자리에 떨어뜨림"""
        if self.hands[self.selected] is None:
            slot = self.selected
        elif None in self.hands:
            slot = self.hands.index(None)
        else:
            slot = self.selected
            self.put_down(self.hands[slot], item.x, item.y)
        self.receive(item, slot)

    def take_from(self, ped):
        """거치대의 UI 를 손으로. 손이 꽉 차면 선택한 슬롯의 UI 를 대신 거치대에 올림"""
        item = ped.take()
        if self.hands[self.selected] is None:
            slot = self.selected
        elif None in self.hands:
            slot = self.hands.index(None)
        else:
            slot = self.selected
            ped.place(self.hands[slot])
        self.receive(item, slot)

    def receive(self, item, slot):
        """UI 를 손 슬롯에 넣고 on_receive 로 알려 줌 (적 UI 획득·도난 UI 회수 점수 등)"""
        item.owner = 'player'
        self.hands[slot] = item
        if Player.on_receive:
            Player.on_receive(item)

    def eat(self):
        """선택한 슬롯의 UI 먹기 (F): 먹는 동작을 시작하고, 손이 입에 닿는 순간 실제로 먹음"""
        item = self.hands[self.selected]
        if item is None or self.busy():
            return
        self.using = item
        if self.facing in ('up', 'down'):
            self.facing = 'right' if self.aim_x >= self.x else 'left'
        self.set_state('eat')

    def swallow(self):
        """내 UI 는 체력 회복, 적 UI·가짜 UI 는 체력 감소. 먹은 UI 는 사라짐.
        (먹는 도중 맞아서 UI 를 떨어뜨렸으면 아무 일도 없음)"""
        item, self.using = self.using, None
        if item is None or item not in self.hands:
            return
        if item.is_fake or item.is_enemy_ui:
            self.hp = max(0, self.hp - EAT_AMOUNT)
        else:
            self.hp = min(MAX_HP, self.hp + EAT_AMOUNT)
        self.hands[self.hands.index(item)] = None
        item.destroy()

    def throw(self):
        """선택한 슬롯의 UI 를 마우스 쪽으로 던짐 (Q): 던지는 동작을 시작하고, 팔을 뻗는 순간 날아감"""
        item = self.hands[self.selected]
        if item is None or self.busy():
            return
        self.using = item
        self.facing = 'right' if self.aim_x >= self.x else 'left'
        self.set_state('throw')

    def release(self):
        """손에서 놓는 순간: 그때 마우스가 가리키는 곳으로 날아감. 던진 UI 는 이 스테이지에서 사라짐"""
        item, self.using = self.using, None
        if item is None or item not in self.hands:
            return
        self.hands[self.hands.index(item)] = None
        item.destroy()
        hand = self.x + (36 if self.facing == 'right' else -36)       # 뻗은 손 위치에서 출발
        game_world.add_object(ThrownUI(item, hand, self.y, self.aim_x, self.aim_y - GUN_HEIGHT), 1)

    def put_down(self, item, x, y):
        if self.blocked(x, y):            # 벽·건물 안이면 발밑에 놓음
            x, y = self.x, self.y
        item.owner = 'floor'
        item.x, item.y = x, y

    def set_aim(self, wx, wy):
        self.aim_x, self.aim_y = wx, wy

    def start_reload(self):
        if self.reload_t <= 0 and self.ammo < MAX_AMMO:
            self.reload_t = RELOAD_TIME

    def fire(self):
        if self.busy() or self.reload_t > 0 or self.fire_cool > 0:
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

    # ---------- 피격 ----------
    def take_hit(self, damage):
        """적에게 맞음. 대시 중이나 맞은 직후에는 무시. 실제로 맞았으면 True"""
        if self.invincible or self.hurt_t > 0 or self.hp <= 0:
            return False
        self.hp = max(0, self.hp - damage)
        self.hurt_t = HURT_INVINCIBLE
        held = [i for i, h in enumerate(self.hands) if h is not None]
        if held and random.random() < HURT_DROP_CHANCE:      # 맞으면 가끔 UI 를 놓침
            i = random.choice(held)
            ox = random.choice((-1, 1)) * random.uniform(30, 50)
            self.put_down(self.hands[i], self.x + ox, self.y + random.uniform(-15, 15))
            self.hands[i] = None
        return True

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

    def speed(self):
        """UI 를 많이 들수록 느려짐 (무게 패널티)"""
        n = sum(1 for h in self.hands if h is not None)
        return PLAYER_SPEED * WEIGHT_SPEED[n]

    def move_dir(self):
        dx = sum(MOVE_KEYS[k][0] for k in self.held)
        dy = sum(MOVE_KEYS[k][1] for k in self.held)
        return dx, dy

    def set_state(self, s):
        if s != self.state:
            self.state = s
            self.t = 0.0
            if s not in ('eat', 'throw'):
                self.using = None             # 대시로 끊으면 먹기·던지기는 없던 일

    # ---------- 갱신 ----------
    def update(self):
        dt = game_framework.frame_time
        self.t += dt
        self.dash_cool = max(0.0, self.dash_cool - dt)
        self.hurt_t = max(0.0, self.hurt_t - dt)
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
        if self.state in ACTIONS:                    # 줍기·사격·먹기·던지기 동안은 제자리
            sheet, t = self.sprites[self.state], self.t * ACTIONS[self.state]
            if self.using is not None:
                if self.state == 'eat' and sheet.frame_at(t) >= EAT_FRAME:
                    self.swallow()
                elif self.state == 'throw' and sheet.frame_at(t) >= THROW_FRAME:
                    self.release()
            if not sheet.finished(t):
                return
            self.set_state('idle')                   # 동작이 끝난 프레임부터 바로 다시 걸을 수 있음
        dx, dy = self.move_dir()
        if dx or dy:
            n = math.hypot(dx, dy)
            v = self.speed()
            self.try_move(dx / n * v * dt, dy / n * v * dt)
            self.walk_t += dt * WALK_CADENCE * v / PLAYER_SPEED   # 움직인 거리만큼 발걸음이 돎 (느려지면 발도 느리게)
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

    def draw(self):
        if self.hurt_t > 0 and int(self.hurt_t * 16) % 2:    # 맞은 직후 깜빡임
            return
        sx, sy = camera.to_screen(self.x, self.y)
        shadow.draw(sx, sy + 2, 46 * camera.Z)
        scale = CHAR_SCALE * camera.Z
        suffix, flip = self.view()
        if self.state == 'dash':                     # 대시는 옆모습 한 종류
            sheet, flip = self.sprites['dash'], self.facing == 'left'
            speed = sheet.duration / DASH_TIME          # 대시 한 번에 달리기 한 바퀴가 딱 돌도록
            sheet.draw(sheet.frame_at(self.t * speed), sx, sy, scale, flip)
            return
        if self.state in ACTIONS:                    # 줍기·사격·먹기·던지기는 옆모습
            sheet = self.sprites[self.state]
            sheet.draw(sheet.frame_at(self.t * ACTIONS[self.state]), sx, sy, scale, self.facing == 'left')
            return
        sheet = self.sprites[f'{self.state}_{suffix}']
        if self.state == 'walk':     # 시트마다 장 수가 달라도(24·28·32장) 한 바퀴 도는 시간은 같게
            frame = int(self.walk_t % 1.0 * sheet.frames)
        else:
            frame = sheet.frame_at(self.t)
        sheet.draw(frame, sx, sy, scale, flip)
