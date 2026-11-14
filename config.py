SCREEN_W, SCREEN_H = 1280, 720
ZOOM = 2.0                 # 카메라 확대 배율 (월드 1px → 화면 2px)
TITLE = 'Lost Interface'

# 캐릭터
CHAR_SCALE = 0.3           # 시트 원본 키 약 256px → 화면 약 77px
PLAYER_SPEED = 220         # px/s
DASH_TIME = 0.28           # 대시 지속 시간 (이 동안 무적)
DASH_SPEED = 3.2           # 기본 속도의 배수
DASH_COOLDOWN = 3.0        # 대시 후 다시 쓰기까지 걸리는 시간 (초)

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

# 플레이어 체력
MAX_HP = 100
HURT_INVINCIBLE = 0.8      # 맞은 뒤 잠깐 무적 (연속으로 맞지 않게)

# 적 공통 (PRD 2.5)
ENEMY_SPEED_MUL = 1.2      # 적은 보안관 기본 속도보다 빠름
HIT_SLOW_MUL = 0.5         # 맞으면 잠시 느려짐
HIT_SLOW_TIME = 1.5
VIEW_DIST = 380            # 시야 거리 (월드 px)
VIEW_ANGLE = 120           # 시야 각도 (도)

# 갱단원 근접 공격
GRUNT_DAMAGE = 12
GRUNT_REACH = 58           # 이 거리 안(가로)에 들어오면 칼을 휘두름
GRUNT_ATTACK_SPEED = 2.0   # 공격 동작 재생 배속
GRUNT_HIT_FRAME = 21       # 칼이 앞으로 나가는 장면 (이때 맞음)
GRUNT_ATTACK_COOL = 0.6    # 한 번 휘두른 뒤 쉬는 시간
