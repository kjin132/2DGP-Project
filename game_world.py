# 레이어: 0 바닥, 1 월드 오브젝트(y 정렬), 2 HUD
world = [[], [], []]


def add_object(o, depth=1):
    world[depth].append(o)


def add_objects(ol, depth=1):
    world[depth] += ol


def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return
    raise ValueError('존재하지 않는 객체를 지우려고 함')


def update():
    for layer in world:
        for o in layer[:]:
            o.update()


def render():
    for depth, layer in enumerate(world):
        if depth == 1:
            # 위쪽(먼 곳)에 있는 것부터 그려서 앞에 있는 것이 뒤를 가리게
            for o in sorted(layer, key=lambda o: -getattr(o, 'sort_y', o.y)):
                o.draw()
        else:
            for o in layer:
                o.draw()


def clear():
    for layer in world:
        layer.clear()
