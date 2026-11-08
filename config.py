SCREEN_W, SCREEN_H = 1280, 720
ZOOM = 2.0                 # 카메라 확대 배율 (월드 1px → 화면 2px)
TITLE = 'Lost Interface'

# 캐릭터
CHAR_SCALE = 0.3           # 시트 원본 키 약 256px → 화면 약 77px
PLAYER_SPEED = 220         # px/s
DASH_TIME = 0.28           # 대시 지속 시간 (이 동안 무적)
DASH_SPEED = 3.2           # 기본 속도의 배수
DASH_COOLDOWN = 0.6

# 사격
BULLET_SPEED = 900
BULLET_LIFE = 1.2
BULLET_SIZE = (8, 16)      # 화면에 그릴 총알 크기
MAX_AMMO = 9
RELOAD_TIME = 1.2
FIRE_INTERVAL = 0.25

# UI 오브젝트
ITEM_WORLD_SIZE = 64       # 바닥에 놓인 UI 의 긴 변 길이 (px)
PICK_RANGE = 70            # E 키가 닿는 거리
