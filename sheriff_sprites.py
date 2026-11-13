from sprite import SpriteSheet

# (파일, 칸 크기, 열 수, 프레임 수, 발 위치, 반복)  — 캐릭터 키 약 256px, 24fps
_SPECS = {
    'idle_side':  ('idle_side.png', 143, 262, 11, 33, (66, 260), True),
    'idle_front': ('idle_front.png', 196, 271, 10, 50, (112, 269), True),
    'idle_back':  ('idle_back.png', 173, 267, 13, 49, (71, 264), True),
    'walk_side':  ('walk_side.png', 189, 273, 24, 24, (109, 271), True),
    'walk_front': ('walk_front.png', 162, 266, 14, 28, (86, 263), True),
    'walk_back':  ('walk_back.png', 174, 273, 16, 32, (83, 265), True),
    'dash':       ('dash.png', 310, 274, 10, 20, (105, 271), True),
    'shoot':      ('shoot.png', 509, 264, 7, 27, (155, 262), False),
    'pickup':     ('pickup.png', 215, 262, 10, 20, (73, 259), False),
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
