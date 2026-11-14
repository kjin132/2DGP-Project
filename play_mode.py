from pico2d import *
import game_framework
import game_world
from player import Player
from body import Body
from background import Background
from collision import CollisionMap
from overlay import OverlaySet
from bullet import Bullet
from ui_item import ITEM_CLASSES
from pedestal import UIPedestal
from hud import HUD
from grunt import Grunt
import pathfind
import stage1
import camera
from config import SCREEN_H

player = None
background = None
items = []
pedestals = []
hud = None
enemies = []
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
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            player.set_aim(*camera.to_world(event.x, SCREEN_H - 1 - event.y))
            player.fire()
        else:
            player.handle_event(event)


def init():
    global player, background, items, pedestals, hud, enemies
    background = Background(stage1.FOLDER)
    game_world.add_object(background, 0)
    camera.set_bounds(background.pixel_w, background.pixel_h)
    collision = CollisionMap(stage1.FOLDER)
    overlays = OverlaySet(stage1.FOLDER)
    game_world.extra_sources.append(overlays.visible)    # 건물 윗부분이 캐릭터를 가리게
    Body.collision = Bullet.collision = collision
    pathfind.build(collision)          # 적 길찾기 격자 (맵마다 한 번)
    items = [ITEM_CLASSES[k](x, y) for k, x, y in stage1.build_items()]
    game_world.add_objects(items, 1)
    Player.items = items
    pedestals = [UIPedestal(x, y) for x, y in stage1.build_pedestals()]
    game_world.add_objects(pedestals, 1)
    Body.pedestals = pedestals
    Bullet.obstacles = pedestals
    enemies = [Grunt(x, y) for x, y in stage1.build_grunts()]
    game_world.add_objects(enemies, 1)
    player = Player(*stage1.PLAYER_START)
    game_world.add_object(player, 1)
    hud = HUD(player, items, pedestals, f'{stage1.FOLDER}/minimap.png', background.pixel_w, background.pixel_h)
    game_world.add_object(hud, 2)
    hide_cursor()      # 마우스 커서 대신 조준선 UI 가 있어야 조준점이 보임


def finish():
    game_world.clear()


def update():
    game_world.update()
    camera.follow(player.x, player.y + 40)
    player.set_aim(*camera.to_world(*mouse_screen))
    hud.mouse = mouse_screen   # 카메라가 움직여도 조준점이 마우스를 따라가게


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def pause():
    pass


def resume():
    pass
