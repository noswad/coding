import os
import pygame

def save_high_score(score, filename="highscore.txt"):
    """將最高分數寫入檔案。"""
    try:
        with open(filename, "w") as f:
            f.write(str(score))
    except Exception as e:
        print(f"無法儲存最高分: {e}")

def load_high_score(filename="highscore.txt"):
    """從檔案讀取最高分數。"""
    try:
        with open(filename, "r") as f:
            return int(f.read())
    except Exception:
        return 0

def rects_collide(rect1, rect2):
    """判斷兩個 pygame.Rect 是否碰撞。"""
    return rect1.colliderect(rect2)

def masks_collide(mask1, mask2, offset):
    """判斷兩個 pygame.mask 是否碰撞。"""
    if mask1 and mask2:
        return mask1.overlap(mask2, offset) is not None
    return False

def resource_path(filename, base_dir=None):
    """取得資源檔案的絕對路徑。"""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)

def clamp(val, min_val, max_val):
    """將數值限制在指定範圍內。"""
    return max(min_val, min(val, max_val))