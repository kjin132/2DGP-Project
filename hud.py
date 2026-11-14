"""켜져 있는(손에 들었거나 거치대에 올린) UI 만 화면에 그리는 HUD"""
from pico2d import load_image, load_font
import math
import game_framework
import camera
from config import SCREEN_W, SCREEN_H, MAX_HP


def _img(name):
    return load_image(f'resources/ui/{name}.png')


class HUD:
    def __init__(self, player, items, pedestals, map_image, map_w, map_h):
        self.player, self.items, self.pedestals = player, items, pedestals
        self.map_image = load_image(map_image)       # 맵 그림을 줄인 것
        self.map_w, self.map_h = map_w, map_h
        self.mouse = (0, 0)
        self.t = 0.0
        self.font = load_font('resources/font/Galmuri11.ttf', 22)
        self.big_font = load_font('resources/font/Galmuri11.ttf', 33)
        self.alert_font = load_font('resources/font/Galmuri11.ttf', 30)
        self.hp_frame, self.hp_fill = _img('item_hp_frame'), _img('item_hp_fill')
        self.minimap = _img('item_minimap')
        self.crosshair = _img('item_crosshair')
        self.aim_dot = _img('aim_dot')
        self.aim_dot.opacify(0.7)
        self.ammo_frame = _img('item_ammo_frame')
        self.bullet = load_image('resources/effect/bullet.png')
        self.score_frame = _img('item_score_frame')
        self.dots = {k: _img('mm_' + k) for k in ('player', 'item', 'pedestal', 'enemy', 'thief', 'exit')}
        self.enemies = []            # 살아 있는 적 (play_mode 가 채워 줌)
        self.exit_gate = None        # 이번 판의 출구 (play_mode 가 채워 줌)
        self.score = None            # 점수 (play_mode 가 채워 줌)
        self.slot = _img('slot')
        self.alerts = []                    # 화면 가운데 위에 잠깐 뜨는 알림 [글자, 색, 남은 시간]
        self.arrow = _img('arrow')
        self.pointers = []                  # 화면 밖 대상을 가리키는 화살표 [대상, 남은 시간]

    def active_kinds(self):
        return {i.kind for i in self.items if i.active and not i.is_fake}

    def alert(self, text, color=(255, 90, 70), time=2.5):
        self.alerts.append([text, color, time])

    def update(self):
        self.t += game_framework.frame_time
        for a in self.alerts:
            a[2] -= game_framework.frame_time
        self.alerts = [a for a in self.alerts if a[2] > 0]
        for p in self.pointers:
            p[1] -= game_framework.frame_time
        self.pointers = [p for p in self.pointers if p[1] > 0 and p[0].alive]

    def point_at(self, target, time=4.0):
        self.pointers.append([target, time])

    def draw_pointers(self):
        """화면 밖에 있는 대상 쪽 화면 가장자리에 깜빡이는 화살표"""
        for target, left in self.pointers:
            if int(left * 4) % 2:
                continue
            sx, sy = camera.to_screen(target.x, target.y + 40)
            if 0 <= sx <= SCREEN_W and 0 <= sy <= SCREEN_H:
                continue                                    # 화면 안에 보이면 화살표 없음
            cx, cy = SCREEN_W / 2, SCREEN_H / 2
            a = math.atan2(sy - cy, sx - cx)
            m = 50
            k = min((SCREEN_W / 2 - m) / max(abs(math.cos(a)), 1e-6), (SCREEN_H / 2 - m) / max(abs(math.sin(a)), 1e-6))
            self.arrow.composite_draw(a, '', cx + math.cos(a) * k, cy + math.sin(a) * k, 56, 56)
    def draw_alerts(self):
        y = SCREEN_H - 190
        for text, color, left in self.alerts[-3:]:
            if left < 0.6 and int(left * 10) % 2:          # 사라지기 전 깜빡임
                continue
            w = sum(30 if ord(ch) > 0x2E80 else 15 for ch in text)
            x = SCREEN_W / 2 - w / 2
            for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):     # 어두운 테두리 (배경·캐릭터 위에서도 읽히게)
                self.alert_font.draw(x + ox, y + oy, text, (40, 20, 10))
            self.alert_font.draw(x, y, text, color)
            y -= 40

    # ---------- 각 UI ----------
    def draw_hp(self):
        W = 320                                   # 화면에 그릴 틀 가로 길이
        s = W / self.hp_frame.w
        h = self.hp_frame.h * s
        cx, cy = 16 + W / 2, SCREEN_H - 16 - h / 2
        # 틀 그림 안의 빈 칸: 왼쪽 위 기준 x 234~578, y 70~111
        left = cx - W / 2 + 234 * s
        bottom = cy + h / 2 - 111 * s
        slot_w, slot_h = (578 - 234) * s, (111 - 70) * s
        self.hp_frame.draw(cx, cy, W, h)          # 틀 먼저, 게이지는 빈 칸 위에
        ratio = max(0.0, self.player.hp / MAX_HP)
        if ratio > 0:
            # 게이지 그림의 막대 부분: 왼쪽 위 기준 x 19~288, y 22~70
            src_w = int(269 * ratio)
            self.hp_fill.clip_draw_to_origin(19, self.hp_fill.h - 70, src_w, 48,
                                             left, bottom, slot_w * ratio, slot_h)

    def draw_minimap(self):
        S = 220
        cx, cy = SCREEN_W - 16 - S / 2, SCREEN_H - 16 - S / 2
        k = S / self.minimap.w
        self.minimap.draw(cx, cy, S, self.minimap.h * k)
        # 양피지 안쪽: 왼쪽 위 기준 x 160~815, y 159~818
        left = cx - S / 2 + 160 * k
        top = cy + self.minimap.h * k / 2 - 159 * k
        iw, ih = (815 - 160) * k, (818 - 159) * k
        # 맵이 가로로 길어서 양피지 안에 비율을 지켜 넣고 위아래는 가운데 정렬
        mw = iw
        mh = iw * self.map_h / self.map_w
        top -= (ih - mh) / 2
        iw, ih = mw, mh
        self.map_image.draw(left + iw / 2, top - ih / 2, iw, ih)
        mx = lambda x: left + x / self.map_w * iw
        my = lambda y: top - ih + y / self.map_h * ih
        for p in self.pedestals:
            self.dots['pedestal'].draw(mx(p.x), my(p.y), 8, 8)
        for i in self.items:
            if i.owner == 'floor':
                self.dots['item'].draw(mx(i.x), my(i.y), 8, 8)
        for e in self.enemies:                  # 적 위치 (PRD 2.3 미니맵: 적 위치)
            if e.who != 'thief':
                self.dots['enemy'].draw(mx(e.x), my(e.y), 7, 7)
        if self.exit_gate is not None:          # 출구 (화면 밖의 출구는 미니맵에만 보임, PRD 2.12)
            g = self.exit_gate
            s = 13 + 2 * math.sin(self.t * 4)
            self.dots['exit'].draw(mx(g.x), my(g.y), s, s)
        self.dots['player'].draw(mx(self.player.x), my(self.player.y), 10, 10)

    def draw_ammo(self):
        W = 280
        s = W / self.ammo_frame.w
        h = self.ammo_frame.h * s
        cx, cy = 16 + W / 2, 16 + h / 2
        self.ammo_frame.draw(cx, cy, W, h)
        # 탄 칸 9개: 왼쪽 위 기준 x 88 + 72*i (너비 64), y 100~211
        for i in range(self.player.ammo):
            x = cx - W / 2 + (88 + 72 * i + 32) * s
            y = cy + h / 2 - 155.5 * s
            self.bullet.draw(x, y, 64 * s * 0.75, 111 * s * 0.9)
        if self.player.reload_t > 0:
            self.font.draw(cx - W / 2, cy + h / 2 + 14, '재장전...', (255, 230, 170))

    def draw_score(self):
        W = 150
        s = W / self.score_frame.w
        h = self.score_frame.h * s
        cx, cy = SCREEN_W / 2, SCREEN_H - 12 - h / 2
        self.score_frame.draw(cx, cy, W, h)
        text = f'{self.score.value:,}'
        # 숫자는 SCORE 글자 아래 (그림 위쪽 기준 y 약 640)
        self.big_font.draw(cx - len(text) * 9.3, cy + h / 2 - 640 * s, text, (60, 30, 20))
        sc = self.score
        info = f'블라인드 x{sc.blind_mult():.1f}'
        if sc.combo >= 2:
            info = f'{sc.combo} 콤보 x{sc.combo_mult():.1f}   ' + info
        self.font.draw(cx - len(info) * 6.5, cy - h / 2 - 14, info, (255, 230, 160))

    def draw_crosshair(self):
        self.crosshair.draw(*self.mouse, 48, 48)

    def draw_aim_dot(self):
        """조준선 UI 가 없을 때는 마우스 위치에 작은 점만 (방향만 알 수 있게)"""
        self.aim_dot.draw(*self.mouse, 10, 10)

    def draw_slots(self):
        """손 슬롯 2칸, 선택한 칸 강조 (PRD 2.1)"""
        size, gap = 64, 10
        x0 = SCREEN_W / 2 - size - gap / 2
        y = 16 + size / 2
        for i in range(2):
            cx = x0 + size / 2 + i * (size + gap)
            sel = (i == self.player.selected)
            self.slot.opacify(1.0 if sel else 0.6)
            self.slot.draw(cx, y, size + (6 if sel else 0), size + (6 if sel else 0))
            item = self.player.hands[i]
            if item:
                k = (size - 14) / max(item.image.w, item.image.h)
                item.image.draw(cx, y, item.image.w * k, item.image.h * k)
            self.font.draw(cx - size / 2 + 4, y + size / 2 - 10, str(i + 1), (255, 235, 180) if sel else (170, 160, 140))
        self.slot.opacify(1.0)
        if self.player.hands[self.player.selected]:      # 고른 칸에 UI 가 있으면 쓸 수 있는 키 안내
            self.font.draw(x0 + 2 * size + gap + 12, y, 'F 먹기  Q 던지기', (255, 235, 180))

    def draw_prompt(self):
        """E 키 안내: 가까운 대상 위에 "E: 줍기" 같은 문구"""
        action, target = self.player.interaction_target()
        if not action:
            return
        label = {'pickup': '줍기', 'take': '줍기', 'install': '설치', 'drop': '내려놓기'}[action]
        tx, ty = (target.x, target.y) if target is not None else (self.player.x, self.player.y)
        sx, sy = camera.to_screen(tx, ty)
        text = f'E: {label}'
        if action == 'pickup':
            text += f' ({target.name})'
        self.font.draw(sx - len(text) * 6, sy + 110 * camera.Z, text, (255, 240, 200))

    def draw(self):
        self.draw_pointers()
        self.draw_alerts()
        self.draw_slots()
        self.draw_prompt()
        kinds = self.active_kinds()
        if 'hp' in kinds:
            self.draw_hp()
        if 'minimap' in kinds:
            self.draw_minimap()
        if 'ammo' in kinds:
            self.draw_ammo()
        if 'score' in kinds:
            self.draw_score()
        if 'crosshair' in kinds:
            self.draw_crosshair()
        else:
            self.draw_aim_dot()
