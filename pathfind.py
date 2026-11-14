"""적이 건물을 돌아서 목표까지 가는 길 찾기 (A*, 16px 칸)
충돌 격자(4px)에서 '몸 충돌 상자가 들어갈 수 있는 칸'만 골라 길찾기 격자를 만든다."""
import heapq
import math
from collision import WALK
from body import BODY_HALF_W, BODY_BOX_H

N = 16          # 길찾기 칸 크기 (월드 px)


class NavGrid:
    def __init__(self, cmap):
        c = cmap.cell
        gw, gh = cmap.gw, cmap.gh
        # 4px 칸 한 줄씩 '막힌 칸 개수' 누적합 → 가로 구간이 비었는지 바로 알 수 있음
        pref = []
        for gy in range(gh):
            row = cmap.data[gy * gw:(gy + 1) * gw]
            acc, p = 0, [0]
            for v in row:
                acc += (v != WALK)
                p.append(acc)
            pref.append(p)
        self.w, self.h = gw * c // N, gh * c // N
        hw = BODY_HALF_W // c + 1
        hh = BODY_BOX_H // c + 1
        self.ok = bytearray(self.w * self.h)
        for ny in range(self.h):
            cy = (ny * N + N // 2) // c
            for nx in range(self.w):
                cx = (nx * N + N // 2) // c
                l, r = cx - hw, cx + hw + 1
                if l < 0 or r > gw or cy < 0 or cy + hh > gh:
                    continue
                if all(pref[y][r] - pref[y][l] == 0 for y in range(cy, cy + hh)):
                    self.ok[ny * self.w + nx] = 1

    def walkable(self, nx, ny):
        return 0 <= nx < self.w and 0 <= ny < self.h and self.ok[ny * self.w + nx]

    def to_cell(self, x, y):
        return int(x // N), int(y // N)

    def nearest_open(self, nx, ny, r=6):
        """막힌 칸이면 가까운 걸을 수 있는 칸으로"""
        if self.walkable(nx, ny):
            return nx, ny
        for d in range(1, r + 1):
            for dx in range(-d, d + 1):
                for dy in (-d, d):
                    if self.walkable(nx + dx, ny + dy):
                        return nx + dx, ny + dy
                    if self.walkable(nx + dy, ny + dx):
                        return nx + dy, ny + dx
        return None

    def find(self, x0, y0, x1, y1, limit=20000):
        """월드 좌표 길(점 목록)을 돌려줌. 못 찾으면 None"""
        s = self.nearest_open(*self.to_cell(x0, y0))
        g = self.nearest_open(*self.to_cell(x1, y1))
        if s is None or g is None:
            return None
        W = self.w
        dist = {s: 0.0}
        came = {}
        heap = [(0.0, s)]
        steps = 0
        while heap:
            _, cur = heapq.heappop(heap)
            if cur == g:
                break
            steps += 1
            if steps > limit:
                return None
            cx, cy = cur
            for dx, dy, cost in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
                                 (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)):
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < W and 0 <= ny < self.h and self.ok[ny * W + nx]):
                    continue
                if dx and dy and not (self.ok[cy * W + nx] and self.ok[ny * W + cx]):
                    continue                    # 모서리를 대각선으로 뚫고 지나가지 않게
                nd = dist[cur] + cost
                if nd < dist.get((nx, ny), 1e18):
                    dist[(nx, ny)] = nd
                    came[(nx, ny)] = cur
                    h = math.hypot(g[0] - nx, g[1] - ny)
                    heapq.heappush(heap, (nd + h, (nx, ny)))
        if g not in dist:
            return None
        cells = [g]
        while cells[-1] != s:
            cells.append(came[cells[-1]])
        cells.reverse()
        pts = [(cx * N + N / 2, cy * N + N / 2) for cx, cy in cells]
        pts[-1] = (x1, y1) if self.walkable(*self.to_cell(x1, y1)) else pts[-1]
        return pts[1:] if len(pts) > 1 else pts


nav = None


def build(cmap):
    global nav
    nav = NavGrid(cmap)
    return nav
