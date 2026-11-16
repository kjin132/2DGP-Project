from sprite import SpriteSheet

# (파일, 칸 크기, 열 수, 프레임 수, 발 위치, 반복)  — 캐릭터 키 약 256px, 24fps
_SPECS = {
    'idle_side':  ('idle_side.png', 143, 262, 11, 33, (88, 260), True),
    'idle_front': ('idle_front.png', 196, 271, 10, 50, (112, 269), True),
    'idle_back':  ('idle_back.png', 152, 262, 8, 33, (67, 259), True),
    'walk_side':  ('walk_side.png', 189, 273, 24, 24, (106, 271), True),
    'walk_front': ('walk_front.png', 162, 266, 14, 28, (86, 263), True),
    'walk_back':  ('walk_back.png', 174, 273, 16, 32, (83, 265), True),
    'dash':       ('run_side.png', 196, 268, 8, 16, (137, 259), True),     # 대시는 달리기 그림
    'shoot':      ('shoot.png', 308, 262, 8, 31, (90, 259), False),
    'shoot_front': ('shoot_front.png', 180, 260, 8, 26, (93, 258), False),   # 시트 22번 장면부터 (총을 겨눈 자세)
    'shoot_back':  ('shoot_back.png', 214, 258, 8, 32, (72, 256), False),    # 시트 18번 장면부터
    'throw_front': ('throw_front.png', 184, 260, 8, 53, (99, 258), False),
    'throw_back':  ('throw_back.png', 216, 266, 8, 82, (122, 262), False),
    'pickup':     ('pickup.png', 215, 262, 10, 20, (85, 259), False),
    'eat':        ('eat.png', 168, 264, 8, 73, (85, 262), False),
    'throw':      ('throw.png', 226, 262, 8, 47, (96, 261), False),
    'death':      ('death.png', 384, 220, 8, 66, (142, 205), False),      # 이 시트만 0.8배로 줄여 저장돼 있음
}

# 옆모습: 대기 그림은 걷기보다 자세가 낮게(모자 챙 높이 221 vs 228) 그려져 있어서 3% 키워서 맞춤.
# 발 위치 x 는 머리와 발 가운데가 같은 자리에 오도록 잡음 (서 있다 걸을 때 몸이 옆으로 튀지 않게)
# 사격 그림은 다리를 벌리고 선 자세라 키가 250px 로 가장 작게 그려져 있어 5% 키움 (모자 높이가 걷기와 같아짐).
# 줍기도 대기와 같은 자세로 시작하므로 같은 3%
# 달리기 그림은 머리(모자 챙 너비 106px)가 다른 동작(113px)보다 작게 그려져 있어 7% 키움
# 뒤 대기 그림은 키가 4px 작게 그려져 있어 2% 키움 (모자 높이가 뒤 걷기와 같아짐)
# 앞·뒤 사격 그림은 총을 들어 올리는 앞부분이 길어서(옆 사격의 3배) 겨눈 자세부터 재생:
# 그러면 총구 불꽃이 옆 사격과 같은 9장 뒤에 나오고 동작 길이도 비슷해짐
_FIRST = {'shoot_front': 22, 'shoot_back': 18}
# 뒤 던지기 그림은 키는 같은데 몸이 가로로 홀쭉하게 그려져 있음 (모자 챙 99px, 뒤 대기는 113px).
# 키는 3% 키우고 가로는 11% 더 늘려 뒤 대기·걷기와 같은 비율로
_STRETCH = {'throw_back': 1.11}
# 옆 대기와 옆 걷기는 다리 길이가 달라 벨트(버클) 높이가 10px 차이 남 (발에서 대기 104, 걷기 114).
# 둘 다 109 에 오도록 대기는 다리를 조금 늘리고 걷기는 조금 줄임 (모자 높이는 그대로)
_LEGS = {'idle_side': (101, 1.048), 'walk_side': (114, 0.956)}
_SIZE = {'throw_back': 1.03, 'shoot_back': 1.02, 'idle_back': 1.02, 'idle_side': 1.03, 'dash': 1.07, 'shoot': 1.05, 'pickup': 1.03, 'eat': 1.03, 'throw': 1.03, 'death': 1.29}

# 옆 걷기 그림은 장면마다 몸 전체가 좌우로 최대 9px 씩 튀어서(머리 위치 기준) 걸을 때 뚝뚝 끊겨 보임.
# 그림은 그대로 두고, 머리가 늘 같은 자리에 오도록 프레임마다 밀어서 그림
_SHIFT = {'walk_side': (6, 6, 5, 5, -1, -1, -2, -3, -1, -1, 6, 6, 6, 6, 4, 4, 4, 3, 3, 4, 4, 3, 6, 5)}

_cache = None


def load():
    global _cache
    if _cache is None:
        _cache = {}
        for name, (f, w, h, cols, n, anchor, loop) in _SPECS.items():
            _cache[name] = SpriteSheet('resources/sheriff/' + f, w, h, cols, n, anchor,
                                       loop=loop, pingpong=(name == 'idle_front'),
                                       size=_SIZE.get(name, 1.0), shift=_SHIFT.get(name), first=_FIRST.get(name, 0), stretch=_STRETCH.get(name, 1.0),
                                       legs=_LEGS.get(name))
    return _cache
