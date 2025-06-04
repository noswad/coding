import os

# --- 視窗與 FPS ---
WIDTH = 1024
HEIGHT = 768
FPS = 60

# --- 顏色定義 (Colors) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)
DARK_GRAY = (40, 40, 40)

# --- 字型大小比例 ---
UI_FONT_SIZE_SMALL_RATIO = 0.03
UI_FONT_SIZE_MEDIUM_RATIO = 0.045
UI_FONT_SIZE_LARGE_RATIO = 0.06

# --- 遊戲設定 ---
PLAYER_LIVES_START = 3
BOSS_APPEAR_ROUND = 7
PLAYER_SHOOT_INTERVAL_SEC = 0.1333
DIVE_INTERVAL_SEC = 3.0
STAR_COUNT_BASE = 100

# --- 敵人生成參數 ---
ENEMY_START_Y_RATIO = 0.1
ENEMY_ROW_SPACING_RATIO = 0.1
ENEMY_COL_SPACING_RATIO = 0.125
ENEMY_ELITE_OFFSET_Y_RATIO = 0.1083
NUM_NORMAL_ROWS = 3
NUM_COLS = 6

# --- 物件大小比例 ---
PLAYER_SIZE_RATIO = (0.0625, 0.0833)
ENEMY_SIZE_RATIO = (0.05, 0.0667)
PLAYER_BULLET_SIZE_RATIO = (0.01875, 0.05)
COCOA_BULLET_SIZE_RATIO = (0.01875, 0.0416)
ELITE_ENEMY_SIZE_RATIO = (0.05625, 0.075)
BOSS_LV1_SIZE_RATIO = (0.15, 0.1667)
BOSS_BULLET_SIZE_RATIO = (0.04, 0.0533)

# --- UI 元素位置與大小比例 ---
UI_SCORE_POS_RATIO = (0.0125, 0.0166)
UI_LIVES_OFFSET_X_RATIO = 0.0125
UI_ROUND_POS_Y_OFFSET_RATIO = 0.0417

# --- 星星背景設定 ---
STAR_COUNT = 60

# --- 遊戲狀態 ---
from enum import Enum, auto
class GameState(Enum):
    START = auto()
    PLAYING = auto()
    BOSS_INTRO_SEQUENCE = auto()
    BOSS_FIGHT = auto()
    PLAYER_DYING = auto()
    GAME_OVER = auto()

# --- 資源路徑 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = "images"  # 改為相對目錄名稱
SOUND_DIR = "sounds"  # 改為相對目錄名稱
FONT_DIR  = "fonts"   # 改為相對目錄名稱 (為求一致性)

# --- 其他 ---
TITLE = "太空貓咪大戰外星生物"
ICON_PATH = os.path.join(BASE_DIR, IMAGE_DIR, "icon.png") # 使用 BASE_DIR 組合路徑
HIGH_SCORE_FILE = "highscore.txt"

# --- BOSS 進場動畫相關 ---
MAX_BOSS_INTRO_TIME_STAGE_1_FRAMES = int(FPS * 1.5)
MAX_BOSS_INTRO_TIME_STAGE_2_FRAMES = int(FPS * 2.0)
MAX_BOSS_INTRO_TIME_STAGE_3_FRAMES = int(FPS * 1.0)
SCREEN_FLASH_DURATION_FRAMES = int(FPS * 0.15)

# --- 玩家射擊間隔（以 frame 為單位）---
PLAYER_SHOOT_INTERVAL_FRAMES = int(FPS * PLAYER_SHOOT_INTERVAL_SEC)
DIVE_INTERVAL_FRAMES = int(FPS * DIVE_INTERVAL_SEC)