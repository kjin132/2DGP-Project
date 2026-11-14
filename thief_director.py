"""무법자 도둑 등장 관리: 일정 시간마다, 훔칠 UI 가 있을 때 맵 가장자리에서 한 명씩 나타남 (PRD 2.10)"""
import math
import random
import game_framework
import game_world
from body import Body
from enemy import Enemy
from thief import Thief
from config import THIEF_FIRST_DELAY, THIEF_INTERVAL, THIEF_SPAWN_MIN_DIST


class ThiefDirector:
    def __init__(self, player, spawns):
        self.player = player
        self.spawns = spawns
        self.timer = THIEF_FIRST_DELAY
        self.thief = None
        self.on_appear = None           # 나타났을 때 부를 함수 (경고 표시)

    def something_to_steal(self):
        return any(p.item is not None for p in Body.pedestals) or any(self.player.hands)

    def spawn(self):
        p = self.player
        far = [s for s in self.spawns if math.hypot(s[0] - p.x, s[1] - p.y) >= THIEF_SPAWN_MIN_DIST]
        gate = Thief.exit_gate
        if gate is not None:          # 출구 바로 옆에서 나오면 훔치고 곧장 빠져나가 버리므로 뺌
            far = [s for s in far if math.hypot(s[0] - gate.x, s[1] - gate.y) >= 900] or far
        x, y = random.choice(far or self.spawns)
        self.thief = Thief(x, y)
        game_world.add_object(self.thief, 1)
        Enemy.group.append(self.thief)
        if self.on_appear:
            self.on_appear(self.thief)

    def update(self):
        if self.thief is not None:
            if self.thief in Enemy.group:          # 아직 살아서 맵에 있음
                return
            self.thief = None                       # 쓰러졌거나 나갔음 → 다음 도둑 대기
            self.timer = THIEF_INTERVAL
        self.timer -= game_framework.frame_time
        if self.timer <= 0 and self.something_to_steal():
            self.spawn()

    def draw(self):
        pass
