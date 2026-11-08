"""켜져 있는(손에 들었거나 거치대에 올린) UI 만 화면에 그리는 HUD"""
from pico2d import load_image, load_font
import camera
from config import SCREEN_W, SCREEN_H, MAX_HP


def _img(name):
    return load_image(f'resources/ui/{name}.png')


class HUD:
    def __init__(self, player, items):
        self.player, self.items = player, items
        self.font = load_font('resources/font/Galmuri11.ttf', 22)
        self.hp_frame, self.hp_fill = _img('item_hp_frame'), _img('item_hp_fill')
        self.slot = _img('slot')

    def active_kinds(self):
        return {i.kind for i in self.items if i.active and not i.is_fake}

    def update(self):
        pass

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
        self.draw_slots()
        self.draw_prompt()
        kinds = self.active_kinds()
        if 'hp' in kinds:
            self.draw_hp()
