"""점수 (PRD 2.9): 점수판 UI 가 켜져 있을 때만 쌓이고,
최종 점수 = 기본 점수 × 콤보 배율 × 블라인드 배율. 도둑을 놓친 감점은 점수판이 없어도 깎임."""
import game_framework

COMBO_WINDOW = 3.0          # 이 시간 안에 다음 적을 쓰러뜨리면 콤보가 이어짐
COMBO_STEPS = ((10, 2.5), (6, 2.0), (3, 1.5), (1, 1.0))
BLIND_MULT = {4: 1.0, 3: 1.2, 2: 1.4, 1: 1.6, 0: 2.0}
BLIND_KINDS = ('hp', 'minimap', 'crosshair', 'ammo')     # 점수판을 뺀 플레이어 UI 4종


class Score:
    def __init__(self, items):
        self.items = items          # 지금 스테이지의 UI 전부
        self.value = 0
        self.combo = 0
        self.combo_t = 0.0
        self.max_combo = 0

    # ---------- 켜진 UI ----------
    def board_active(self):
        """진짜 점수판이 켜져 있어야 점수가 쌓임 (가짜 점수판은 쌓이는 척만 함)"""
        return any(i.kind == 'score' and i.active and not i.is_fake for i in self.items)

    def blind_count(self):
        kinds = {i.kind for i in self.items if i.active and not i.is_fake and i.kind in BLIND_KINDS}
        return len(kinds)

    def combo_mult(self):
        for n, m in COMBO_STEPS:
            if self.combo >= n:
                return m
        return 1.0

    def blind_mult(self):
        return BLIND_MULT[self.blind_count()]

    # ---------- 점수 ----------
    def add(self, base):
        """배율을 곱해 더함. 점수판이 꺼져 있으면 0. 실제로 더한 점수를 돌려줌"""
        if not self.board_active():
            return 0
        gained = int(round(base * self.combo_mult() * self.blind_mult()))
        self.value += gained
        return gained

    def kill(self, base, window=COMBO_WINDOW):
        """적 처치: 콤보를 잇고 점수를 더함"""
        self.combo = self.combo + 1 if self.combo_t > 0 else 1
        self.max_combo = max(self.max_combo, self.combo)
        self.combo_t = window
        return self.add(base)

    def penalty(self, amount):
        """점수판과 관계없이 깎임"""
        self.value = max(0, self.value - amount)

    def update(self):
        if self.combo_t > 0:
            self.combo_t -= game_framework.frame_time
            if self.combo_t <= 0:
                self.combo = 0
