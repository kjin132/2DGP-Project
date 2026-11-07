from sprite import SpriteSheet

# (파일, 칸 크기, 열 수, 프레임 수, 발 위치, 반복)  — 캐릭터 키 약 256px, 24fps
_SPECS = {
    'idle_side':  ('idle_side.png', 142, 260, 11, 33, (65, 259), True),
    'idle_front': ('idle_front.png', 201, 269, 10, 50, (108, 268), True),
    'idle_back':  ('idle_back.png', 172, 265, 13, 49, (70, 263), True),
    'walk_side':  ('walk_side.png', 195, 283, 24, 24, (111, 282), True),
    'walk_front': ('walk_front.png', 162, 265, 14, 28, (58, 262), True),
    'walk_back':  ('walk_back.png', 175, 271, 16, 32, (84, 264), True),
    'dash':       ('dash.png', 325, 273, 10, 20, (121, 270), True),
    'shoot':      ('shoot.png', 466, 261, 7, 27, (124, 260), False),
}

_cache = None


def load():
    global _cache
    if _cache is None:
        _cache = {}
        for name, (f, w, h, cols, n, anchor, loop) in _SPECS.items():
            _cache[name] = SpriteSheet('resources/sheriff/' + f, w, h, cols, n, anchor,
                                       loop=loop, pingpong=(name == 'idle_front'))
    return _cache
