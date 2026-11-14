from pico2d import *
import game_framework
import game_world
from player import Player
from body import Body
from background import Background
from collision import CollisionMap
from overlay import OverlaySet
from bullet import Bullet
from thrown_ui import ThrownUI
from ui_item import ITEM_CLASSES, UIItem
from pedestal import UIPedestal
from hud import HUD
from grunt import Grunt
from enemy import Enemy
import pathfind
import random
from exit_gate import ExitGate
from score import Score
from thief import Thief
from thief_director import ThiefDirector
import stage1
import camera
from config import SCREEN_H

player = None
background = None
items = []
pedestals = []
hud = None
enemies = []
exit_gate = None
score = None
thieves = None
mouse_screen = (0, 0)     # 마우스 화면 좌표 (pico2d 기준, 아래가 0)


def handle_events():
    global mouse_screen
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_screen = (event.x, SCREEN_H - 1 - event.y)
            player.set_aim(*camera.to_world(*mouse_screen))    # 같은 프레임에 누른 Q·클릭도 새 위치로
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            player.set_aim(*camera.to_world(event.x, SCREEN_H - 1 - event.y))
            player.fire()
        else:
            player.handle_event(event)


def init():
    global player, background, items, pedestals, hud, enemies, exit_gate, score, thieves
    background = Background(stage1.FOLDER)
    game_world.add_object(background, 0)
    camera.set_bounds(background.pixel_w, background.pixel_h)
    collision = CollisionMap(stage1.FOLDER)
    overlays = OverlaySet(stage1.FOLDER)
    game_world.extra_sources.append(overlays.visible)    # 건물 윗부분이 캐릭터를 가리게
    Body.collision = Bullet.collision = ThrownUI.collision = collision
    pathfind.build(collision)          # 적 길찾기 격자 (맵마다 한 번)
    exit_gate = ExitGate(*random.choice(stage1.EXIT_CANDIDATES))
    game_world.add_object(exit_gate, 1)
    items = [ITEM_CLASSES[k](x, y) for k, x, y in stage1.build_items()]
    game_world.add_objects(items, 1)
    Player.items = UIItem.all = items
    score = Score(items)
    Enemy.score = score
    score.chasing = lambda: any(t.state == 'flee' for t in Enemy.group if t.who == 'thief')
    pedestals = [UIPedestal(x, y) for x, y in stage1.build_pedestals()]
    game_world.add_objects(pedestals, 1)
    Body.pedestals = pedestals
    for ped in pedestals:
        pathfind.nav.block_rect(*ped.get_bb())
    Bullet.obstacles = pedestals
    enemies = [Grunt(x, y) for x, y in stage1.build_grunts()]
    game_world.add_objects(enemies, 1)
    Enemy.group = enemies
    Bullet.targets = ThrownUI.targets = enemies
    player = Player(*stage1.PLAYER_START)
    game_world.add_object(player, 1)
    Enemy.target = player
    Enemy.drop_pool = [k for k, c in ITEM_CLASSES.items() if c.is_enemy_ui]
    Enemy.on_drop = on_enemy_ui_drop
    Player.on_receive = on_receive
    Enemy.show_hp = lambda: 'enemy_hp' in hud.active_kinds()
    Enemy.show_alarm = lambda: 'enemy_alarm' in hud.active_kinds()
    Thief.exit_gate = exit_gate
    Thief.on_steal = on_thief_steal
    Thief.on_escape = on_thief_escape
    Thief.leave_trail = lambda: 'minimap' not in hud.active_kinds()
    thieves = ThiefDirector(player, stage1.THIEF_SPAWNS)
    thieves.on_appear = on_thief_appear
    game_world.add_object(thieves, 0)
    hud = HUD(player, items, pedestals, f'{stage1.FOLDER}/minimap.png', background.pixel_w, background.pixel_h)
    hud.score = score
    hud.enemies = Enemy.group
    hud.exit_gate = exit_gate
    game_world.add_object(hud, 2)
    hide_cursor()      # 마우스 커서 대신 조준선 UI 가 있어야 조준점이 보임


def eul(word):
    """'을/를' 고르기: 마지막 글자에 받침이 있으면 '을'"""
    ch = word[-1]
    if '가' <= ch <= '힣':
        return word + ('을' if (ord(ch) - 0xAC00) % 28 else '를')
    return word + '를'


def on_enemy_ui_drop(kind, x, y):
    """맞은 적 옆 바닥에 적 UI 가 떨어짐 (몸에 가리지 않게 조금 옆, 막힌 곳이면 발밑)"""
    item = ITEM_CLASSES[kind](x, y - 4)
    for dx in (36, -36):
        if not player.blocked(x + dx, y - 4):
            item.x = x + dx
            break
    items.append(item)
    game_world.add_object(item, 1)
    hud.alert(f'{item.name} 떨어짐!', (150, 220, 255), 2.5)


def on_receive(item):
    """UI 가 보안관 손에 들어올 때마다"""
    if not item.claimed:
        item.claimed = True
        on_claim(item)
    if item.stolen_at is not None:
        on_recover(item)


def on_recover(item):
    """도둑에게 빼앗긴 UI 를 되찾음 (PRD 2.10 추격 보상)
    +300, 5초 안에 되찾으면 +200, 미니맵 없이 흔적만으로 되찾으면 +300"""
    fast = score.clock - item.stolen_at <= 5.0
    by_trail = not item.seen_on_map          # 미니맵 없이 빛 흔적만 따라가 되찾음
    item.stolen_at = None
    score.recovered += 1
    base = 300 + (200 if fast else 0) + (300 if by_trail else 0)
    gained = score.add(base)
    text = f'{item.name} {"빠른 " if fast else ""}회수!'
    if gained:
        text += f'  +{gained}'
        score.popup(player.x, player.y + 20, f'+{gained}', (140, 255, 160))
    hud.alert(text, (140, 255, 160), 3.0)
    hud.turn_on(item.kind)
    if by_trail:
        hud.alert('흔적만으로 찾아냈다!', (255, 230, 140), 3.0)


def on_claim(item):
    """적 UI 를 처음 손에 넣으면 +500 (PRD 2.9 적 UI 획득)"""
    if item.is_enemy_ui:
        gained = score.add(500)
        if gained:
            score.popup(player.x, player.y + 20, f'+{gained}', (150, 220, 255))
        hud.alert(f'{eul(item.name)} 손에 넣었다!', (150, 220, 255), 2.5)


def on_thief_appear(thief):
    hud.alert('무법자 도둑 출현!', (255, 200, 80), 3.0)
    hud.point_at(thief)


def on_thief_steal(thief, item):
    item.stolen_at = score.clock
    item.seen_on_map = False
    hud.alert(f'{item.name} 도난!')


def on_thief_escape(thief, item):
    """도둑이 UI 를 들고 나가면 그 UI 는 이 스테이지에서 잃고 500점 깎임 (점수판이 없어도)"""
    score.penalty(500)
    name = item.name if item else 'UI'
    hud.alert(f'도둑이 {eul(name)} 가지고 달아났다!  -500', (255, 120, 90), 3.5)


def finish():
    game_world.clear()


def update():
    game_world.update()
    score.update()
    if 'minimap' in hud.active_kinds():
        for i in items:
            if i.stolen_at is not None:
                i.seen_on_map = True
    camera.follow(player.x, player.y + 40)
    player.set_aim(*camera.to_world(*mouse_screen))
    hud.mouse = mouse_screen   # 카메라가 움직여도 조준점이 마우스를 따라가게
    if exit_gate.reached(player):
        bonus = clear_bonus()
        end_stage('clear', [f'{exit_gate.name} 출구로 빠져나왔다', f'끝까지 지킨 UI 보너스 +{bonus:,}'])
    elif player.hp <= 0:
        end_stage('gameover', ['보안관이 쓰러졌다'])


def draw_world():
    game_world.render()


def draw():
    clear_canvas()
    draw_world()
    update_canvas()


def kept_items():
    """끝까지 지킨 내 UI: 손에 들었거나 거치대에 올려 둔 것 (적 UI 는 빼고)"""
    return [i for i in items if i.owner in ('player', 'pedestal') and not i.is_enemy_ui]


def clear_bonus():
    """스테이지 클리어: 남은 UI 1개당 +300, 내구도 100% 인 UI 1개당 +200 더 (PRD 2.9)"""
    kept = kept_items()
    base = 300 * len(kept) + 200 * sum(1 for i in kept if i.durability >= 100)
    return score.add(base)


def end_stage(kind, lines):
    """클리어·게임 오버: 결과 화면을 위에 띄움 (점수·처치·최대 콤보·되찾은 UI)"""
    import result_mode
    lines = lines + [f'처치 {score.kills}   최대 콤보 {score.max_combo}   되찾은 UI {score.recovered}',
                     f'최종 점수 {score.value:,}']
    result_mode.info = {'kind': kind, 'lines': lines}
    game_framework.push_mode(result_mode)


def pause():
    pass


def resume():
    hide_cursor()
