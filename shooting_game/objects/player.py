import pygame
import resources

class Player:
    def __init__(self, x_ratio, y_ratio):
        # 設定主角的寬高
        self.width = 64
        self.height = 64

        # 以背景圖尺寸計算初始座標
        bg_w = resources.background_img.get_width() if resources.background_img else 1024
        bg_h = resources.background_img.get_height() if resources.background_img else 768
        self.x = int(x_ratio * bg_w)
        self.y = int(y_ratio * bg_h)

        # 載入並縮放圖片
        self.image = None
        if resources.player_img:
            try:
                img = resources.player_img.convert_alpha()
                self.image = pygame.transform.smoothscale(img, (self.width, self.height))
            except Exception as e:
                print(f"[Player] 圖片縮放失敗: {e}")
                self.image = None

        # 建立 rect，中心點為 (self.x, self.y)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x, self.y)
        self.lives = 3

    def update_position(self, x=None, y=None):
        """可選擇性地更新 x/y 並同步 rect"""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # 除錯：顯示主角座標
        # print(f"Player draw at {self.rect.topleft}, image={self.image is not None}")
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (0, 255, 0), self.rect)