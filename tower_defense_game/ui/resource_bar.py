import pygame
import time

class ResourceManager:
    def __init__(self, initial=100, auto_gain=25, interval=5.0):
        """
        initial: 初始資源
        auto_gain: 每次自動增加的資源量
        interval: 自動增加間隔（秒）
        """
        self.amount = initial
        self.auto_gain = auto_gain
        self.interval = interval
        self.last_gain_time = time.time()

    def update(self):
        now = time.time()
        if now - self.last_gain_time >= self.interval:
            self.amount += self.auto_gain
            self.last_gain_time = now

    def can_afford(self, cost):
        return self.amount >= cost

    def spend(self, cost):
        if self.can_afford(cost):
            self.amount -= cost
            return True
        return False

    def add(self, value):
        self.amount += value

    def get_amount(self):
        return self.amount

class ResourceBar:
    def __init__(self, resource_manager, font_size=32):
        self.resource_manager = resource_manager
        self.font = pygame.font.SysFont("Arial", font_size)
        self.bar_rect = pygame.Rect(600, 10, 180, 50)  # 右上角
        self.bg_color = (255, 255, 180)
        self.text_color = (80, 60, 0)
        self.button_rect = pygame.Rect(620, 70, 60, 40)  # 植物按鈕
        self.button_color = (200, 255, 200)
        self.button_text = "Plant"
        self.button_cost = 50  # 假設建置植物花費

    def update(self):
        self.resource_manager.update()

    def draw(self, screen):
        # 畫資源條背景
        pygame.draw.rect(screen, self.bg_color, self.bar_rect, border_radius=10)
        # 畫資源數字
        amount = self.resource_manager.get_amount()
        text = self.font.render(f"Sun: {amount}", True, self.text_color)
        screen.blit(text, (self.bar_rect.x + 20, self.bar_rect.y + 10))

        # 畫植物按鈕
        pygame.draw.rect(screen, self.button_color, self.button_rect, border_radius=8)
        btn_text = self.font.render(self.button_text, True, (0, 100, 0))
        screen.blit(btn_text, (self.button_rect.x + 2, self.button_rect.y + 5))
        # 畫花費
        cost_text = self.font.render(str(self.button_cost), True, (255, 120, 0))
        screen.blit(cost_text, (self.button_rect.x + 10, self.button_rect.y + 25))

    def handle_event(self, event):
        """
        處理點擊植物按鈕。
        如果成功花費資源，回傳 True，表示玩家已選擇購買植物。
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                if self.resource_manager.spend(self.button_cost):
                    print("資源條：已選擇植物，等待放置。")
                    return True
                else:
                    print("資源條：資源不足，無法選擇植物。")
        return False

# --- 單元測試 ---
def _test_resource_bar():
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    rm = ResourceManager(initial=50, auto_gain=10, interval=2)
    bar = ResourceBar(rm)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            bar.handle_event(event)

        bar.update()
        screen.fill((0, 100, 200))
        bar.draw(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    _test_resource_bar()