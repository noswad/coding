# config.py
import os

# 專案根目錄
# __file__ 是 d:\coding\tower_defense_game\config.py
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 格子大小
CELL_WIDTH = 80
CELL_HEIGHT = 100

# 冷卻時間（毫秒）
PLANT_COOLDOWN = 2000

# 遊戲區域格數
GRID_ROWS = 5
GRID_COLS = 9

# 初始資源
INITIAL_RESOURCES = 100

# 其他參數可依需求擴充