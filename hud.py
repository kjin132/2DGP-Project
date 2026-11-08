"""켜져 있는(손에 들었거나 거치대에 올린) UI 만 화면에 그리는 HUD"""
from pico2d import load_image, load_font
from config import SCREEN_W


def _img(name):
    return load_image(f'resources/ui/{name}.png')


class HUD:
    def __init__(self, player, items):
        self.player, self.items = player, items
        self.font = load_font('resources/font/Galmuri11.ttf', 22)
        self.slot = _img('slot')

    def active_kinds(self):
        return {i.kind for i in self.items if i.active and not i.is_fake}

    def update(self):
        pass

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

    def draw(self):
        self.draw_slots()

