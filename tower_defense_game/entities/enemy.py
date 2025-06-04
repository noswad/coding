import pygame
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Should resolve to d:/coding/tower_defense_game

class Enemy(pygame.sprite.Sprite):
    IMAGE_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "zombie.png")

    def __init__(self, pos, hp=100, speed=1, attack_power=10,
                 attack_interval=1.0):
        super().__init__()
        try:
            self.image = pygame.image.load(self.IMAGE_PATH).convert_alpha()
        except Exception:
            self.image = pygame.Surface((60, 80))
            self.image.fill((120, 120, 120))
        self.rect = self.image.get_rect(midleft=pos)
        self.hp = hp
        self.speed = speed
        self.attack_power = attack_power
        self.attack_interval = attack_interval
        self.last_attack_time = 0
        self.is_attacking = False
        self.target_plant = None

    def update(self, plants, current_time, game_over_callback=None):
        # 確保此簽名正確
        if self.hp <= 0:
            self.kill()
            return

        # 檢查是否碰到任何 Plant
        collided_plant = None
        for plant in plants:
            # plant.rect 需由外部傳入（通常為格子 rect）
            if self.rect.colliderect(plant.rect):
                collided_plant = plant
                break

        if collided_plant:
            self.is_attacking = True
            self.target_plant = collided_plant
            # 攻擊間隔
            if current_time - self.last_attack_time >= self.attack_interval:
                self.target_plant.take_damage(self.attack_power)
                self.last_attack_time = current_time
        else:
            self.is_attacking = False
            self.target_plant = None
            self.rect.x -= self.speed  # 向左移動

        # 檢查是否到達畫面左側
        if self.rect.right < 0:
            print("Game Over! Enemy reached the left side.")
            if game_over_callback:
                game_over_callback()
            self.kill()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# --- 測試用 Plant stub ---
class PlantStub:
    def __init__(self, rect, hp=50):
        self.rect = rect
        self.hp = hp

    def take_damage(self, amount):
        self.hp -= amount
        print(f"Plant 被攻擊，剩餘 HP: {self.hp}")


# --- 單元測試 ---
def _test_enemy_group():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # 建立一個 PlantStub
    plant_rect = pygame.Rect(300, 200, 60, 80)
    plant = PlantStub(plant_rect)
    plants = [plant]

    # 建立敵人群組
    enemies = pygame.sprite.Group()
    enemy = Enemy(pos=(700, 240), hp=30, speed=5)
    enemies.add(enemy)

    running = True
    while running:
        current_time = pygame.time.get_ticks() / 1000  # 秒
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        # 更新與繪製
        enemies.update(plants, current_time)
        for e in enemies:
            e.draw(screen)
        pygame.draw.rect(screen, (0, 255, 0), plant.rect, 2)
        pygame.display.flip()
        clock.tick(30)

        # 測試結束條件
        if not enemies or plant.hp <= 0:
            print("測試結束")
            running = False

    pygame.quit()


if __name__ == "__main__":
    _test_enemy_group()