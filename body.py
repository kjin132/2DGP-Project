"""맵 위를 걸어 다니는 것(보안관, 적)이 함께 쓰는 이동·충돌 처리"""
import camera
from collision import overlaps

BODY_HALF_W = 17       # 몸통 너비의 절반 (월드 px)
BODY_BOX_H = 22        # 충돌 상자 높이 (발끝 ~ 무릎)


class Body:
    collision = None    # 맵 충돌 격자, play_mode 가 채워 줌
    pedestals = []      # 거치대 목록 (거치대도 지나갈 수 없음)

    def body_bb(self, x=None, y=None):
        """충돌 상자: 좌우는 몸통 양끝, 아래는 발끝, 위는 무릎 높이.
        오른쪽으로 가다 부딪히면 몸 오른쪽 끝, 왼쪽은 왼쪽 끝, 아래는 발끝이 닿는 순간 멈춘다.
        위쪽을 머리까지 잡으면 건물 사이 길(약 72px)을 키(약 77px)가 못 지나가서 무릎 높이까지만."""
        x = self.x if x is None else x
        y = self.y if y is None else y
        return x - BODY_HALF_W, y, x + BODY_HALF_W, y + BODY_BOX_H

    def blocked(self, x, y):
        bb = self.body_bb(x, y)
        if Body.collision and Body.collision.blocks_walk(*bb):
            return True
        return any(overlaps(bb, p.get_bb()) for p in Body.pedestals)

    def try_move(self, dx, dy):
        """x, y 를 따로 움직여 보고 막히면 그 축만 취소 (벽을 따라 미끄러지듯).
        실제로 움직였는지 돌려줌"""
        moved = False
        if dx and not self.blocked(self.x + dx, self.y):
            self.x += dx
            moved = True
        if dy and not self.blocked(self.x, self.y + dy):
            self.y += dy
            moved = True
        return moved

    def clamp_to_map(self):
        self.x = min(max(self.x, 20), camera.map_w - 20)
        self.y = min(max(self.y, 10), camera.map_h - 60)
