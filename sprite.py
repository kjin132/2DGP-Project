from pico2d import load_image


class SpriteSheet:
    """가로 cols 칸짜리 스프라이트 시트 한 장 = 애니메이션 하나.
    anchor 는 칸 왼쪽 위 기준 발 위치(x, y). 그릴 때는 발 위치를 월드 좌표에 맞춘다."""

    def __init__(self, path, w, h, cols, frames, anchor, fps=24, loop=True, pingpong=False, size=1.0, shift=None, first=0, stretch=1.0, legs=None):
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
        # 다리 길이 보정: (벨트 높이 그림 px, 다리 배율). 발~벨트는 이 배율로, 벨트~모자는 키가 그대로가 되게 반대로 늘리고 줄임
        self.legs = legs
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
        fl = 'h' if flip else ''
        if self.legs:
            belt, mul = self.legs
            foot = self.h - self.ay                       # 셀 아래쪽에서 발까지 (그림 px)
            yb = foot + belt                              # 셀 아래쪽에서 벨트까지
            top = self.ay                                 # 발에서 셀 위쪽까지
            lo = scale * mul
            hi = scale * (top - belt * mul) / (top - belt)
            base = y - foot * lo                          # 아래쪽 조각의 바닥
            self.image.clip_composite_draw(left, bottom, self.w, yb, 0, fl,
                                           x + dx, base + yb * lo / 2, self.w * sx, yb * lo)
            up = self.h - yb
            self.image.clip_composite_draw(left, bottom + yb, self.w, up, 0, fl,
                                           x + dx, base + yb * lo + up * hi / 2, self.w * sx, up * hi)
            return
        self.image.clip_composite_draw(left, bottom, self.w, self.h, 0, fl,
                                       x + dx, y + dy, self.w * sx, self.h * scale)
