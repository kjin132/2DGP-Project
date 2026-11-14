"""갱단원 (Grunt): 플레이어에게 다가와 칼로 근접 공격 (PRD 2.5)"""
import math
import random
from ui_item import UIItem
from body import Body
from config import GRUNT_DAMAGE, GRUNT_REACH, GRUNT_ATTACK_SPEED, GRUNT_HIT_FRAME, GRUNT_ATTACK_COOL
from enemy import Enemy


class Grunt(Enemy):
    who = 'grunt'
    max_hp = 40
    points = 100
    WANDER_RANGE = 350          # 처음 자리에서 이만큼 안에서 돌아다님

    def __init__(self, x, y):
        super().__init__(x, y)
        self.home = (x, y)
        self.goal = None
        self.wait = random.uniform(0.3, 1.5)
        self.last_seen = None           # 마지막으로 본 보안관 위치
        self.replan = 0.0               # 길 다시 잡기까지 남은 시간
        self.attack_cool = 0.0
        self.fetch_item = None          # 주우러 가는 바닥 UI
        self.hit_done = False           # 이번 휘두르기에서 이미 맞혔는지

    def pick_wander_goal(self):
        """처음 자리 주변의 걸을 수 있는 곳 하나 (몇 번 해 보고 못 찾으면 제자리)"""
        for _ in range(12):
            gx = self.home[0] + random.uniform(-self.WANDER_RANGE, self.WANDER_RANGE)
            gy = self.home[1] + random.uniform(-self.WANDER_RANGE, self.WANDER_RANGE)
            if not self.blocked(gx, gy):
                return gx, gy
        return None

    def wander(self, dt):
        if self.goal is None:
            self.moving = False
            self.wait -= dt
            if self.wait <= 0:
                self.goal = self.pick_wander_goal()
                self.wait = random.uniform(0.8, 2.0)
            return
        arrived = self.step_toward(*self.goal, dt, self.speed() * 0.5)   # 돌아다닐 때는 천천히
        if arrived or not self.moving:            # 도착했거나 벽에 막히면 잠깐 쉬었다가 다른 곳으로
            self.goal = None

    def chase(self, dt):
        """보이면 곧장, 건물에 막히면 길찾기로 돌아서 쫓아감"""
        tg = self.target
        self.last_seen = (tg.x, tg.y)
        if self.in_reach():                   # 칼이 닿는 거리면 더 다가가지 않고 마주 봄
            self.moving = False
            self.facing = 'right' if tg.x >= self.x else 'left'
            return
        direct = Body.collision is None or Body.collision.line_clear(self.x, self.y + 10, tg.x, tg.y + 10)
        if self.path:                         # 돌아가는 길을 따라가는 중
            self.replan -= dt
            if self.replan <= 0:
                if direct:
                    self.path = []            # 다시 곧장 가 봄
                else:
                    self.go_to(tg.x, tg.y)
                    self.replan = 0.5
            if self.path:
                self.follow_path(dt)
                return
        if direct:
            self.step_toward(tg.x, tg.y, dt)
            if not self.moving:               # 보이는데 몸이 걸려 못 가면 길찾기로
                self.go_to(tg.x, tg.y)
                self.replan = 0.5
        else:
            self.go_to(tg.x, tg.y)
            self.replan = 0.5
            self.follow_path(dt)

    def spot_floor_ui(self):
        """보이는 곳에 떨어진 내 UI 가 있으면 그것 (모든 적은 바닥 UI 를 주움, PRD 2.11)"""
        if self.carried is not None:
            return None
        for it in UIItem.all:
            if it.owner == 'floor' and not it.is_enemy_ui and self.can_see(it):
                return it
        return None

    def fetch(self, dt):
        it = self.fetch_item
        if it is None or it.owner != 'floor':     # 다른 누가 먼저 주웠음
            self.set_state('wander')
            return
        if math.hypot(it.x - self.x, it.y - self.y) < 24:
            self.carry(it)
            self.set_state('wander')
            self.goal = None
            return
        if self.path_goal != (it.x, it.y):
            self.go_to(it.x, it.y)
        if self.follow_path(dt) and math.hypot(it.x - self.x, it.y - self.y) >= 24:
            self.step_toward(it.x, it.y, dt)

    def in_reach(self):
        tg = self.target
        return abs(tg.x - self.x) < GRUNT_REACH and abs(tg.y - self.y) < 26

    def start_attack(self):
        self.facing = 'right' if self.target.x >= self.x else 'left'
        self.set_state('attack')
        self.hit_done = False
        self.moving = False

    def attack(self, dt):
        """칼 휘두르기: 칼이 앞으로 나가는 장면에 닿아 있으면 맞음"""
        sheet = self.sprites['attack']
        frame = sheet.frame_at(self.t * GRUNT_ATTACK_SPEED)
        if not self.hit_done and frame >= GRUNT_HIT_FRAME:
            self.hit_done = True
            if self.in_reach():
                self.target.take_hit(GRUNT_DAMAGE)
        if sheet.finished(self.t * GRUNT_ATTACK_SPEED):
            self.attack_cool = GRUNT_ATTACK_COOL
            self.set_state('chase')

    def take_hit(self, damage):
        """맞으면 등 뒤에서 쏴도 알아차리고 쫓아옴"""
        super().take_hit(damage)
        if self.alive and self.state in ('wander', 'search') and self.target:
            self.last_seen = (self.target.x, self.target.y)
            self.face_toward(self.target.x - self.x, self.target.y - self.y)
            self.set_state('chase')

    @property
    def winding_up(self):
        """칼을 들어 올리는 중 (적 경보등 UI 가 알려 주는 순간)"""
        return self.state == 'attack' and not self.hit_done

    def search(self, dt):
        """놓치면 마지막으로 본 곳까지 가 본 뒤 다시 돌아다님 (PRD 2.5)"""
        if self.path_goal != self.last_seen:
            if not self.go_to(*self.last_seen):
                self.set_state('wander')
                return
        if self.follow_path(dt):
            self.set_state('wander')
            self.goal = None

    def think(self, dt):
        sees = self.target is not None and self.can_see(self.target)
        if sees and self.state in ('wander', 'search', 'fetch'):
            self.set_state('chase')
        elif not sees and self.state == 'chase' and not self.in_reach():
            self.set_state('search')
        self.attack_cool = max(0.0, self.attack_cool - dt)
        if self.state == 'attack':
            self.attack(dt)
            return
        if self.state == 'chase' and self.attack_cool <= 0 and self.in_reach():
            self.start_attack()
            return
        if self.state in ('wander', 'search'):
            it = self.spot_floor_ui()
            if it is not None:
                self.fetch_item = it
                self.set_state('fetch')
        if self.state == 'fetch':
            self.fetch(dt)
        elif self.state == 'wander':
            self.wander(dt)
        elif self.state == 'chase':
            self.chase(dt)
        elif self.state == 'search':
            self.search(dt)

    def sheet(self):
        if self.state == 'attack':
            return self.sprites['attack'], self.facing == 'left'
        return super().sheet()

    def frame(self, sheet):
        if self.state == 'attack':
            return sheet.frame_at(self.t * GRUNT_ATTACK_SPEED)
        return super().frame(sheet)
