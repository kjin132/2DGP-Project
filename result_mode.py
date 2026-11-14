"""스테이지 클리어 / 게임 오버 화면: 게임 화면 위에 어둡게 덮고 결과를 보여 줌"""
from pico2d import *
import game_framework
import play_mode
from config import SCREEN_W, SCREEN_H

font = None
big = None
dim = None
info = {}           # play_mode 가 채워 줌: kind('clear'/'gameover'), score, lines


def init():
    global font, big, dim
    font = load_font('resources/font/Galmuri11.ttf', 26)
    big = load_font('resources/font/Galmuri11.ttf', 64)
    dim = load_image('resources/ui/dim.png')
    show_cursor()


def finish():
    pass


def handle_events():
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key in (SDLK_RETURN, SDLK_r):
            game_framework.pop_mode()                 # 결과 화면 닫고
            game_framework.change_mode(play_mode)     # 스테이지 처음부터


def update():
    pass


def text_width(text, size):
    """갈무리 폰트 대략 너비: 한글은 글자 크기만큼, 영문·숫자·기호는 절반"""
    return sum(size if ord(ch) > 0x2E80 else size * 0.5 for ch in text)


def center_text(f, y, text, color, size):
    f.draw(SCREEN_W / 2 - text_width(text, size) / 2, y, text, color)


def draw():
    clear_canvas()
    play_mode.draw_world()
    dim.opacify(0.65)
    dim.draw(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H)
    if info.get('kind') == 'clear':
        center_text(big, SCREEN_H / 2 + 120, 'STAGE CLEAR', (255, 220, 120), 64)
    else:
        center_text(big, SCREEN_H / 2 + 120, 'GAME OVER', (230, 70, 60), 64)
    y = SCREEN_H / 2 + 30
    for line in info.get('lines', []):
        center_text(font, y, line, (255, 240, 210), 26)
        y -= 40
    center_text(font, 80, 'Enter: 다시 하기   ESC: 끝내기', (200, 190, 170), 26)
    update_canvas()


def pause():
    pass


def resume():
    pass
