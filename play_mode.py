from pico2d import *
import game_framework
import game_world
from background import Background
import stage1
import camera

background = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()


def init():
    global background
    background = Background(stage1.FOLDER)
    game_world.add_object(background, 0)
    camera.set_bounds(background.pixel_w, background.pixel_h)
    camera.follow(*stage1.PLAYER_START)


def finish():
    game_world.clear()


def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def pause():
    pass


def resume():
    pass
