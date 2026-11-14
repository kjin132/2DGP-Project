"""적 공통: 맵 위를 걷고, 맞으면 느려지고, 쓰러지면 가진 UI 를 떨어뜨린다 (PRD 2.5)"""
import math
import random
import game_framework
import game_world
import camera
import shadow
import enemy_sprites
import pathfind
from pico2d import load_image
from body import Body
from config import CHAR_SCALE, PLAYER_SPEED, ENEMY_SPEED_MUL, VIEW_DIST, VIEW_ANGLE, HIT_SLOW_MUL, HIT_SLOW_TIME
from config import ENEMY_UI_DROP_CHANCE


class Enemy(Body):
    who = None              # 스프라이트 묶음 이름 ('thief' / 'grunt')
    max_hp = 30
    target = None           # 쫓을 대상(보안관), play_mode 가 채워 줌
    group = []              # 살아 있는 적 목록 (총알·미니맵이 함께 씀), play_mode 가 채워 줌
    score = None            # 점수 (play_mode 가 채워 줌)
    points = 100            # 쓰러뜨리면 받는 기본 점수
    CORPSE_TIME = 1.2       # 쓰러진 뒤 사라지기까지
    drop_pool = []          # 이번 스테이지에서 아직 안 떨어진 적 UI 종류 (같은 종류는 한 번만, PRD 2.4)
    on_drop = None          # 적 UI 가 떨어질 때 부를 함수 (종류, x, y), play_mode 가 채워 줌
    show_hp = staticmethod(lambda: False)    # 적 HP 바 UI 가 켜져 있는지, play_mode 가 채워 줌
    hp_frame = hp_fill = None

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.sprites = enemy_sprites.load(self.who)
        self.hp = self.max_hp
        self.facing = 'down'
        self.state = 'wander'
        self.t = 0.0                  # 지금 동작의 재생 시간
        self.moving = False
        self.path = []                # 길찾기로 잡은 지점 목록
        self.path_goal = None
        self.stuck_t = 0.0            # 길을 따라가는데 못 움직인 시간
        self.slow_t = 0.0             # 0 보다 크면 맞아서 느려진 상태
        self.flash_t = 0.0            # 맞은 순간 잠깐 반투명하게
        self.carried = None           # 주운(또는 훔친) 내 UI — 머리 위에 들고 다님

    # ---------- 이동 ----------
    def speed(self):
        v = PLAYER_SPEED * ENEMY_SPEED_MUL
        return v * HIT_SLOW_MUL if self.slow_t > 0 else v

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

    # ---------- 길 따라가기 ----------
    def go_to(self, tx, ty):
        """(tx, ty) 까지 건물을 돌아가는 길을 새로 잡음"""
        self.path = pathfind.nav.find(self.x, self.y, tx, ty) if pathfind.nav else [(tx, ty)]
        self.path_goal = (tx, ty)
        return self.path is not None

    def follow_path(self, dt, speed=None):
        """잡아 둔 길을 따라 한 프레임 이동. 끝까지 갔으면 True"""
        if not self.path:
            return True
        tx, ty = self.path[0]
        if self.step_toward(tx, ty, dt, speed) or math.hypot(tx - self.x, ty - self.y) < 6:
            self.path.pop(0)
        self.stuck_t = 0.0 if self.moving else self.stuck_t + dt
        if self.stuck_t > 0.4 and self.path_goal:      # 걸려서 못 가면 지금 자리에서 길을 다시 잡음
            self.stuck_t = 0.0
            self.go_to(*self.path_goal)
        return not self.path

    # ---------- 피격 ----------
    @property
    def alive(self):
        return self.hp > 0

    def hit_by_point(self, px, py):
        """화면에 그려진 몸(발에서 머리까지) 안에 점이 들어오면 맞음"""
        return abs(px - self.x) < 20 and self.y - 4 <= py <= self.y + 80

    def take_hit(self, damage):
        if not self.alive:
            return
        self.roll_enemy_ui()
        self.hp -= damage
        if self.hp <= 0:
            self.die()
            return
        self.slow_t = HIT_SLOW_TIME           # 맞으면 1.5초 동안 절반 속도 (PRD 2.5)
        self.flash_t = 0.12

    def roll_enemy_ui(self):
        """맞을 때마다 5% 확률로 아직 안 나온 적 UI 하나를 옆 바닥에 떨어뜨림"""
        if Enemy.drop_pool and random.random() < ENEMY_UI_DROP_CHANCE:
            kind = Enemy.drop_pool.pop(random.randrange(len(Enemy.drop_pool)))
            if Enemy.on_drop:
                Enemy.on_drop(kind, self.x, self.y)

    def carry(self, item):
        item.owner = 'enemy'
        self.carried = item

    def drop_carried(self):
        """가진 UI 를 발밑에 떨어뜨림 (내 UI 를 가진 적은 쓰러지면 반드시 떨어뜨림, PRD 2.5)"""
        item, self.carried = self.carried, None
        if item is not None:
            item.owner = 'floor'
            item.x, item.y = self.x, self.y - 6
        return item

    def die(self):
        self.drop_carried()
        if Enemy.score is not None:
            Enemy.score.kill(self.points, self.x, self.y)
        self.hp = 0
        self.set_state('dead')
        self.moving = False
        self.path = []
        if self in Enemy.group:
            Enemy.group.remove(self)

    def set_state(self, s):
        if s != self.state:
            self.state = s
            self.t = 0.0

    def update(self):
        dt = game_framework.frame_time
        self.t += dt
        self.slow_t = max(0.0, self.slow_t - dt)
        self.flash_t = max(0.0, self.flash_t - dt)
        if self.state == 'dead':
            death = self.sprites['death']
            if self.t > death.duration + self.CORPSE_TIME:
                game_world.remove_object(self)
            return
        self.think(dt)

    def think(self, dt):
        """적마다 하는 행동 (하위 클래스에서 정함)"""
        pass

    # ---------- 그리기 ----------
    def sheet(self):
        """지금 그릴 시트와 좌우 반전 여부"""
        if self.state == 'dead':
            return self.sprites['death'], self.facing == 'left'
        if self.facing == 'up':
            return self.sprites['walk_back'], False
        if self.facing == 'down':
            return self.sprites['walk_front'], False
        return self.sprites['walk_side'], self.facing == 'left'

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y)
        sheet, flip = self.sheet()
        fade = 1.0
        if self.state == 'dead':                 # 다 쓰러진 뒤 서서히 사라짐
            over = self.t - sheet.duration
            fade = max(0.0, 1 - over / self.CORPSE_TIME) if over > 0 else 1.0
            if fade < 1:
                sheet.image.opacify(fade)
        else:
            shadow.draw(sx, sy + 2, 46 * camera.Z)
        if self.flash_t > 0:
            sheet.image.opacify(0.45)
        sheet.draw(self.frame(sheet), sx, sy, CHAR_SCALE * camera.Z, flip)
        if self.flash_t > 0 or fade < 1:
            sheet.image.opacify(1.0)
        top = sy + 84 * camera.Z                  # 머리 바로 위
        if self.carried is not None:              # 들고 있는 UI 를 머리 위에 (누가 가져갔는지 보이게)
            self.carried.draw_at(sx, top, ground=False)
            top += 76 * camera.Z
        else:
            top = sy + 74 * camera.Z              # 모자 꼭대기
        if self.alive and Enemy.show_hp():
            self.draw_hp_bar(sx, top)

    def draw_hp_bar(self, sx, bottom_y):
        """적 HP 바 UI 가 켜져 있으면 머리 위에 남은 체력 (해골 틀 + 빨간 막대)"""
        if Enemy.hp_frame is None:
            Enemy.hp_frame = load_image('resources/ui/item_enemy_hp_frame.png')
            Enemy.hp_fill = load_image('resources/ui/item_enemy_hp_fill.png')
        f, g = Enemy.hp_frame, Enemy.hp_fill
        W = 46 * camera.Z
        s = W / f.w
        H = f.h * s
        cy = bottom_y + H / 2 - 30 * s           # 그림 아래 빈 여백만큼 내림
        f.draw(sx, cy, W, H)
        ratio = max(0.0, self.hp / self.max_hp)
        if ratio <= 0:
            return
        # 틀 안의 빈 칸: 왼쪽 위 기준 x 216~604, y 118~188 / 막대 그림의 빨간 부분: x 36~328, y 54~104
        left = sx - W / 2 + 216 * s
        bottom = cy + H / 2 - 188 * s
        g.clip_draw_to_origin(36, g.h - 104, int(292 * ratio), 50,
                              left, bottom, (604 - 216) * s * ratio, (188 - 118) * s)

    def frame(self, sheet):
        if self.state == 'dead':
            return sheet.frame_at(self.t)
        return sheet.frame_at(self.t) if self.moving else 0     # 서 있을 때는 걷기 첫 장면
