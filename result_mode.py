"""스테이지 클리어 / 게임 오버 화면: 게임 화면 위에 어둡게 덮고 결과를 보여 줌"""
from pico2d import *
import game_framework
import play_mode
from config import SCREEN_W, SCREEN_H

font = None
big = None
dim = None
info = {}           # play_mode 가 채워 줌: kind('clear'/'gameover'), score, lines
t = 0.0             # 이 화면이 뜬 뒤 흐른 시간
SHOW_AT = 1.3       # 게임 오버: 쓰러지는 모습이 보이도록 이만큼 뒤부터 어두워지며 글자가 나옴
FADE = 0.6


def init():
    global font, big, dim, t
    t = 0.0
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
        elif e.type == SDL_KEYDOWN and e.key in (SDLK_RETURN, SDLK_r) and shown() >= 1:
            game_framework.pop_mode()                 # 결과 화면 닫고
            game_framework.change_mode(play_mode)     # 스테이지 처음부터


def shown():
    """결과 표시가 얼마나 나타났는지 0~1. 클리어는 바로, 게임 오버는 쓰러진 뒤 서서히"""
    if info.get('kind') != 'gameover':
        return 1.0
    return min(1.0, max(0.0, (t - SHOW_AT) / FADE))


def update():
    global t
    t += game_framework.frame_time
    if info.get('kind') == 'gameover':
        play_mode.update_world()          # 게임 오버 뒤에도 맵은 계속 움직임 (쓰러지는 동작, 돌아다니는 적)


def text_width(text, size):
    """갈무리 폰트 대략 너비: 한글은 글자 크기만큼, 영문·숫자·기호는 절반"""
    return sum(size if ord(ch) > 0x2E80 else size * 0.5 for ch in text)


def center_text(f, y, text, color, size):
    f.draw(SCREEN_W / 2 - text_width(text, size) / 2, y, text, color)


def draw():
    clear_canvas()
    play_mode.draw_world()
    k = shown()
    if k <= 0:
        update_canvas()
        return
    dim.opacify((0.45 if info.get('kind') == 'gameover' else 0.65) * k)   # 게임 오버는 뒤가 잘 보이게 덜 어둡게
    dim.draw(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H)
    if k < 0.5:
        update_canvas()
        return
    if info.get('kind') == 'clear':
        center_text(big, SCREEN_H / 2 + 120, 'STAGE CLEAR', (255, 220, 120), 64)
        y = SCREEN_H / 2 + 30
    else:                                   # 화면 가운데 쓰러진 보안관을 가리지 않게 위쪽에
        center_text(big, SCREEN_H / 2 + 215, 'GAME OVER', (230, 70, 60), 64)
        y = SCREEN_H / 2 + 160
    for line in info.get('lines', []):
        color = (255, 215, 100) if line.startswith('최종 점수') else (255, 240, 210)   # 최종 점수는 금색
        center_text(font, y, line, color, 26)
        y -= 40
    center_text(font, 80, 'Enter: 다시 하기   ESC: 끝내기', (200, 190, 170), 26)
    update_canvas()


def pause():
    pass


def resume():
    pass
