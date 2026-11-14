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
BULLET_DAMAGE = 10
ENEMY_UI_DROP_CHANCE = 0.05   # 적이 맞을 때마다 적 UI 를 떨어뜨릴 확률 (PRD 2.4)

# UI 오브젝트
ITEM_WORLD_SIZE = 64       # 바닥에 놓인 UI 의 긴 변 길이 (px)
PICK_RANGE = 70            # E 키가 닿는 거리
WEIGHT_SPEED = (1.0, 0.9, 0.75)   # 들고 있는 UI 0/1/2개일 때 이동 속도 배율 (PRD 2.2)

# 플레이어 체력
MAX_HP = 100
HURT_INVINCIBLE = 0.8      # 맞은 뒤 잠깐 무적 (연속으로 맞지 않게)
HURT_DROP_CHANCE = 0.3     # 맞으면 들고 있던 UI 하나를 떨어뜨릴 확률 (PRD 2.2)
EAT_AMOUNT = 25            # UI 를 먹으면 회복(또는 적·가짜 UI 면 감소)하는 체력 (최대 체력의 25%)

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

# 무법자 도둑
THIEF_STEAL_SPEED = 1.6    # 훔치는 동작 재생 배속 (약 0.6초)
THIEF_FLEE_MUL = 1.15      # 훔친 뒤 도망갈 때는 더 빠름
THIEF_FIRST_DELAY = 40     # 스테이지 시작 뒤 첫 도둑이 나타나기까지 (초)
THIEF_INTERVAL = 50        # 도둑이 사라진 뒤 다음 도둑까지
THIEF_SPAWN_MIN_DIST = 700 # 보안관과 이만큼은 떨어진 곳에서 나타남

# UI 던지기 (Q)
THROW_SPEED = 650
THROW_RANGE = 420          # 이만큼 날아가면 떨어져 부서짐
THROW_DAMAGE = 35          # 총알 3~4발 정도의 강한 공격
