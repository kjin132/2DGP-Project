"""적 스프라이트 시트 (무법자 도둑, 갱단원). 모두 오른쪽을 보는 그림이고 왼쪽은 뒤집어 그림.
(파일, 칸 크기, 열 수, 프레임 수, 발 위치, 반복, 배율)  — 배율은 서 있는 키를 보안관(약 256px)에 맞춘 값"""
from sprite import SpriteSheet

_SPECS = {
    'thief': {
        'walk_front': ('walk_front.png', 170, 266, 8, 29, (65, 257), True, 1.016),
        'walk_side': ('walk_side.png', 172, 260, 8, 32, (108, 257), True, 1.016),
        'walk_back': ('walk_back.png', 164, 266, 8, 34, (94, 258), True, 1.032),
        'steal': ('steal.png', 218, 262, 8, 24, (109, 260), False, 1.004),
        'death': ('death.png', 344, 280, 8, 39, (139, 263), False, 1.004),
    },
    'grunt': {
        'walk_front': ('walk_front.png', 162, 270, 8, 28, (80, 261), True, 1.0),
        'walk_side': ('walk_side.png', 130, 268, 8, 28, (71, 263), True, 1.0),
        'walk_back': ('walk_back.png', 160, 270, 8, 20, (77, 264), True, 1.004),
        'attack': ('attack.png', 258, 284, 8, 49, (147, 281), False, 1.004),
        'death': ('death.png', 228, 260, 8, 38, (115, 256), False, 1.004),
    },
}

_cache = {}


def load(who):
    """who: 'thief' 또는 'grunt'. 같은 시트는 한 번만 불러와 모든 적이 함께 씀"""
    if who not in _cache:
        _cache[who] = {name: SpriteSheet(f'resources/{who}/{f}', w, h, cols, n, anchor, loop=loop, size=size)
                       for name, (f, w, h, cols, n, anchor, loop, size) in _SPECS[who].items()}
    return _cache[who]
