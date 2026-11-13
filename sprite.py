from pico2d import load_image


class SpriteSheet:
    """가로 cols 칸짜리 스프라이트 시트 한 장 = 애니메이션 하나.
    anchor 는 칸 왼쪽 위 기준 발 위치(x, y). 그릴 때는 발 위치를 월드 좌표에 맞춘다."""

    def __init__(self, path, w, h, cols, frames, anchor, fps=24, loop=True, pingpong=False):
        self.image = load_image(path)
        self.w, self.h = w, h
        self.cols = cols
        self.frames = frames
        self.ax, self.ay = anchor
        self.fps = fps
        self.loop = loop
        self.pingpong = pingpong

    @property
    def duration(self):
        n = self.frames * 2 - 2 if self.pingpong else self.frames
        return n / self.fps

    def frame_at(self, t):
        i = int(t * self.fps)
        if self.pingpong:
            cycle = self.frames * 2 - 2
            i = i % cycle if self.loop else min(i, cycle - 1)
            return i if i < self.frames else cycle - i
        return i % self.frames if self.loop else min(i, self.frames - 1)

    def finished(self, t):
        return not self.loop and t >= self.duration

    def draw(self, i, x, y, scale=1.0, flip=False):
        """i 번째 프레임을 발 위치 (x, y) 에 그림. pico2d 는 아래쪽이 y=0."""
        col, row = i % self.cols, i // self.cols
        left = col * self.w
        bottom = self.image.h - (row + 1) * self.h
        dx = (self.w / 2 - self.ax) * scale
        dy = (self.ay - self.h / 2) * scale
        if flip:
            dx = -dx
        self.image.clip_composite_draw(left, bottom, self.w, self.h, 0, 'h' if flip else '',
                                       x + dx, y + dy, self.w * scale, self.h * scale)
