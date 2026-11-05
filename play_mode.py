from pico2d import *
import game_framework
import game_world
from player import Player
from background import Background
import stage1
import camera

player = None
background = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            player.handle_event(event)


def init():
    global player, background
    background = Background(stage1.FOLDER)
    game_world.add_object(background, 0)
    camera.set_bounds(background.pixel_w, background.pixel_h)
    player = Player(*stage1.PLAYER_START)
    game_world.add_object(player, 1)


def finish():
    game_world.clear()


def update():
    game_world.update()
    camera.follow(player.x, player.y + 40)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def pause():
    pass


def resume():
    pass
