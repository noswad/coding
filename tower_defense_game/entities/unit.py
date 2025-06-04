import pygame
import os
# Local application import, moved before module globals to satisfy E402.
# This relies on sys.path being correctly set by an entry point like core/game.py.
from entities.projectile import Projectile 

# Module global: Determine the project root directory (used for asset paths).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The sys.path manipulation block has been removed as it's redundant
# given core/game.py handles it, and it was causing the E402 error.

class Plant(pygame.sprite.Sprite): # Plant 繼承 pygame.sprite.Sprite
    DEFAULT_IMAGE_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "plant.png")

    def __init__(self, grid_pos, cell_center_pos, hp=100, fire_rate=2.0, damage=20, 
                 name="Plant", color=(0, 200, 0), image_path=None, **other_kwargs):
        """
        grid_pos: (col, row) 在格線中的位置
        cell_center_pos: (x, y) 格子中心的像素座標，用於定位 Sprite
        hp: 植物的生命值
        fire_rate: 發射間隔（秒）
        damage: 子彈攻擊力
        name: 植物的名稱
        color: 用於預留位置圖片的顏色
        image_path: 植物圖片的路徑，如果為 None，則使用 DEFAULT_IMAGE_PATH
        """
        super().__init__() # 初始化 Sprite 父類
        self.grid_pos = grid_pos
        self.fire_rate_ms = fire_rate * 1000 # 轉換為毫秒
        self.damage = damage
        self.hp = hp # 初始化植物的生命值
        self.last_shot_time_ms = pygame.time.get_ticks() # 使用 Pygame 的時間
        self.name = name
        self.color = color
        self.projectiles = []

        # 如果提供了 image_path，則嘗試載入它
        if image_path is not None:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e: # 更具體的錯誤捕捉
                print(f"無法載入植物圖片 '{image_path}': {e}. 使用預留位置圖片。")
                # 為動畫型植物提供正確的預留區域 (80x80)
            self.image = pygame.Surface((80, 80), pygame.SRCALPHA) # Transparent placeholder for animated plants
                # self.image.fill(self.color) # Using a color might be misleading
        else: # 如果 image_path 為 None (如動畫型植物)，建立 80x80 透明預留圖片，不印出警告
            self.image = pygame.Surface((80, 80), pygame.SRCALPHA) # Transparent placeholder for animated plants
        
        self.rect = self.image.get_rect(center=cell_center_pos) # 設定 Sprite 的 rect
    def update(self, enemies): # cell_rect 不再需要，因為有了 self.rect
        if self.hp <= 0:
            self.kill() # 如果生命值耗盡，從所有 Sprite Group 中移除
            return

        # 發射子彈
        if self.fire_rate_ms > 0 and self.damage > 0: # 只有在能造成傷害且有發射速率時才射擊
            current_ticks = pygame.time.get_ticks()
            if current_ticks - self.last_shot_time_ms >= self.fire_rate_ms:
                # 子彈從格子中央右側發射
                x = self.rect.right - 10 # 使用 self.rect
                y = self.rect.centery    # 使用 self.rect
                self.projectiles.append(Projectile((x, y), damage=self.damage))
                self.last_shot_time_ms = current_ticks

        # 更新子彈
        for proj in self.projectiles:
            proj.update(enemies)
        # 移除已消失的子彈
        self.projectiles = [p for p in self.projectiles if not p.is_dead]

    def draw(self, screen): # cell_rect 不再需要
        # 畫植物
        screen.blit(self.image, self.rect) # 使用 self.rect 繪製
        # 畫子彈
        for proj in self.projectiles:
            proj.draw(screen)

    def take_damage(self, amount): # <--- THIS METHOD IS CRUCIAL
        self.hp -= amount
        print(f"Plant at {self.grid_pos} took {amount} damage, HP left: {self.hp}")
        if self.hp <= 0:
            self.kill() # 從 Sprite Group 中移除
