from pico2d import load_image
import camera
import shadow


class UIPedestal:
    """나무통 받침대. UI 1개를 올려 둘 수 있고, 올려 둔 UI 는 맵 어디서든 켜져 있다 (PRD 2.2.3)"""
    image = None
    W = 88                      # 화면에 그릴 가로 크기

    def __init__(self, x, y):
        if UIPedestal.image is None:
            UIPedestal.image = load_image('resources/ui/pedestal.png')
        self.x, self.y = x, y
        self.w = UIPedestal.W
        self.h = UIPedestal.image.h * self.w / UIPedestal.image.w
        self.item = None

    def get_bb(self):
        return self.x - self.w * 0.4, self.y, self.x + self.w * 0.4, self.y + self.h * 0.35

    def blocks_point(self, px, py):
        l, b, r, t = self.get_bb()
        return l <= px <= r and b <= py <= b + self.h * 0.8

    def place(self, item):
        self.item = item
        item.owner = 'pedestal'
        item.x, item.y = self.x, self.y

    def take(self):
        item, self.item = self.item, None
        return item

    def update(self):
        if self.item:
            self.item.update()

    def draw(self):
        sx, sy = camera.to_screen(self.x, self.y)
        Z = camera.Z
        shadow.draw(sx, sy + self.h * 0.14 * Z, self.w * 0.95 * Z, self.h * 0.3 * Z)
        UIPedestal.image.draw(sx, sy + self.h / 2 * Z, self.w * Z, self.h * Z)
        if self.item:
            self.item.draw_at(sx, sy + self.h * 0.72 * Z)     # 통 윗면 위에 올려 그림
