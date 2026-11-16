from pico2d import load_image


class SpriteSheet:
    """가로 cols 칸짜리 스프라이트 시트 한 장 = 애니메이션 하나.
    anchor 는 칸 왼쪽 위 기준 발 위치(x, y). 그릴 때는 발 위치를 월드 좌표에 맞춘다."""

    def __init__(self, path, w, h, cols, frames, anchor, fps=24, loop=True, pingpong=False, size=1.0, shift=None, first=0, stretch=1.0):
        self.image = load_image(path)
        self.w, self.h = w, h
        self.cols = cols
        self.frames = frames
        self.ax, self.ay = anchor
        self.fps = fps
        self.loop = loop
        self.pingpong = pingpong
        self.size = size        # 그림 속 캐릭터 키가 다른 시트와 맞추는 배율 (발 위치 기준)
        self.stretch = stretch  # 가로만 더 늘리는 배율 (캐릭터가 홀쭉하게 그려진 시트를 다른 시트와 같은 비율로)
        self.first = first      # 시트의 이 장면부터 재생 (앞부분을 건너뛸 때)
        self.shift = shift      # 프레임마다 가로로 밀어 그릴 양 (그림 px). 몸이 프레임마다 좌우로 튀는 시트 보정용

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
        scale *= self.size
        k = i + self.first
        col, row = k % self.cols, k // self.cols
        left = col * self.w
        bottom = self.image.h - (row + 1) * self.h
        sx = scale * self.stretch
        dx = (self.w / 2 - self.ax + (self.shift[i] if self.shift else 0)) * sx
        dy = (self.ay - self.h / 2) * scale
        if flip:
            dx = -dx
        self.image.clip_composite_draw(left, bottom, self.w, self.h, 0, 'h' if flip else '',
                                       x + dx, y + dy, self.w * sx, self.h * scale)
