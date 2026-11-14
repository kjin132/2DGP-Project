"""무법자 도둑 (Grabber): 거치대 위의 UI 를 먼저 노려 훔치고, 출구로 빠르게 도망가 그대로 나감 (PRD 2.5, 2.10)
거치대가 비어 있으면 보안관이 들고 있는 UI 를 노린다. 훔친 뒤에는 시야와 관계없이 출구로 간다."""
import math
import random
import game_world
from effects import TrailSpark
from body import Body
from enemy import Enemy
from config import THIEF_STEAL_SPEED, THIEF_FLEE_MUL

STEAL_RANGE = 34


class Thief(Enemy):
    who = 'thief'
    max_hp = 30
    points = 150
    exit_gate = None            # 도망갈 출구 (play_mode 가 채워 줌)
    on_escape = None            # 도둑이 UI 를 들고 나갔을 때 부를 함수
    on_steal = None             # 훔쳤을 때 부를 함수
    leave_trail = None          # 빛 조각 흔적을 남길지 (미니맵이 없을 때만), play_mode 가 채워 줌
    TRAIL_GAP = 0.12

    def __init__(self, x, y):
        super().__init__(x, y)
        self.state = 'approach'
        self.mark = None            # 노리는 거치대 (없으면 보안관)
        self.replan = 0.0
        self.trail_t = 0.0

    # ---------- 노릴 곳 ----------
    def pick_mark(self):
        """UI 가 놓인 거치대 중 가장 가까운 곳. 없으면 None (보안관을 노림)"""
        full = [p for p in Body.pedestals if p.item is not None]
        if not full:
            return None
        return min(full, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))

    def mark_pos(self):
        if self.mark is not None:
            return self.mark.x, self.mark.y - 30          # 거치대 바로 앞
        return self.target.x, self.target.y

    def approach(self, dt):
        if self.mark is not None and self.mark.item is None:
            self.mark = None                           # 그새 보안관이 가져감
        if self.mark is None:
            self.mark = self.pick_mark()
        tx, ty = self.mark_pos()
        if self.mark is None and not any(self.target.hands):
            self.wander_near_player(dt)
            return
        if math.hypot(tx - self.x, ty - self.y) < STEAL_RANGE:
            self.facing = 'right' if (self.mark.x if self.mark else self.target.x) >= self.x else 'left'
            self.set_state('steal')
            self.moving = False
            return
        self.replan -= dt
        if self.replan <= 0 or not self.path:
            self.go_to(tx, ty)
            self.replan = 0.6
        self.follow_path(dt)

    def wander_near_player(self, dt):
        """훔칠 것이 없으면 보안관 주변을 맴돌며 기회를 봄"""
        self.replan -= dt
        if self.replan <= 0 or not self.path:
            a = random.uniform(0, math.tau)
            self.go_to(self.target.x + math.cos(a) * 260, self.target.y + math.sin(a) * 160)
            self.replan = 2.0
        self.follow_path(dt, self.speed() * 0.6)

    # ---------- 훔치기 ----------
    def steal(self, dt):
        sheet = self.sprites['steal']
        if not sheet.finished(self.t * THIEF_STEAL_SPEED):
            return
        item = None
        if self.mark is not None and self.mark.item is not None:
            item = self.mark.take()
        elif self.mark is None and math.hypot(self.target.x - self.x, self.target.y - self.y) < STEAL_RANGE * 1.6:
            held = [i for i, h in enumerate(self.target.hands) if h is not None]
            if held:
                i = random.choice(held)
                item, self.target.hands[i] = self.target.hands[i], None
        if item is None:                               # 한발 늦음: 다시 노림
            self.mark = None
            self.set_state('approach')
            return
        self.carry(item)
        if Thief.on_steal:
            Thief.on_steal(self, item)
        self.set_state('flee')
        self.go_to(self.exit_gate.x, self.exit_gate.y)

    # ---------- 도주 ----------
    def speed(self):
        v = super().speed()
        return v * THIEF_FLEE_MUL if self.state == 'flee' else v

    def flee(self, dt):
        """시야와 관계없이 출구로. 도착하면 UI 를 들고 맵 밖으로 나감"""
        g = self.exit_gate
        if g.reached(self):
            self.escape()
            return
        if not self.path:
            self.go_to(g.x, g.y)
        self.follow_path(dt)
        self.trail_t -= dt
        if self.trail_t <= 0 and self.carried is not None and Thief.leave_trail and Thief.leave_trail():
            self.trail_t = self.TRAIL_GAP
            game_world.add_object(TrailSpark(self.carried.glow, self.x, self.y), 1)

    def escape(self):
        item, self.carried = self.carried, None
        if item is not None:
            item.destroy()
        if self in Enemy.group:
            Enemy.group.remove(self)
        game_world.remove_object(self)
        if Thief.on_escape:
            Thief.on_escape(self, item)

    def think(self, dt):
        if self.state == 'approach':
            self.approach(dt)
        elif self.state == 'steal':
            self.steal(dt)
        elif self.state == 'flee':
            self.flee(dt)

    # ---------- 그리기 ----------
    def sheet(self):
        if self.state == 'steal':
            return self.sprites['steal'], self.facing == 'left'
        return super().sheet()

    def frame(self, sheet):
        if self.state == 'steal':
            return sheet.frame_at(self.t * THIEF_STEAL_SPEED)
        return super().frame(sheet)
