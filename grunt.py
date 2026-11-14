"""갱단원 (Grunt): 플레이어에게 다가와 칼로 근접 공격 (PRD 2.5)"""
import random
import game_framework
from enemy import Enemy


class Grunt(Enemy):
    who = 'grunt'
    max_hp = 40
    WANDER_RANGE = 350          # 처음 자리에서 이만큼 안에서 돌아다님

    def __init__(self, x, y):
        super().__init__(x, y)
        self.home = (x, y)
        self.goal = None
        self.wait = random.uniform(0.3, 1.5)

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

    def update(self):
        super().update()
        dt = game_framework.frame_time
        if self.state == 'wander':
            self.wander(dt)
