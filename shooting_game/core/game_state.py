from enum import Enum, auto

class GameState(Enum):
    START = auto()
    PLAYING = auto()
    BOSS_INTRO_SEQUENCE = auto()
    BOSS_FIGHT = auto()
    PLAYER_DYING = auto()
    GAME_OVER = auto()

# 預設初始狀態
game_state = GameState.START
