from pico2d import *
import game_framework
import game_world
from player import Player
from background import Background
from collision import CollisionMap
from overlay import OverlaySet
from bullet import Bullet
import stage1
import camera
from config import SCREEN_H

player = None
background = None
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
    global player, background
    background = Background(stage1.FOLDER)
    game_world.add_object(background, 0)
    camera.set_bounds(background.pixel_w, background.pixel_h)
    collision = CollisionMap(stage1.FOLDER)
    overlays = OverlaySet(stage1.FOLDER)
    game_world.extra_sources.append(overlays.visible)    # 건물 윗부분이 캐릭터를 가리게
    Player.collision = Bullet.collision = collision
    player = Player(*stage1.PLAYER_START)
    game_world.add_object(player, 1)


def finish():
    game_world.clear()


def update():
    game_world.update()
    camera.follow(player.x, player.y + 40)
    player.set_aim(*camera.to_world(*mouse_screen))


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def pause():
    pass


def resume():
    pass
