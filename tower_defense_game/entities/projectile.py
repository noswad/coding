import pygame
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Should resolve to d:/coding/tower_defense_game

class Projectile(pygame.sprite.Sprite): # Inherit from pygame.sprite.Sprite
    IMAGE_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "projectile.png")
    DEFAULT_SPEED = 5  # Default speed in pixels per frame

    def __init__(self, pos, damage=20, speed=DEFAULT_SPEED, image_surface=None):
        """
        pos: (x, y) 初始座標
        damage: 傷害值
        speed: 每次 update 移動距離 (pixels per frame)
        image_surface: Pre-loaded pygame.Surface for the projectile. Falls back to IMAGE_PATH if None.
        """
        super().__init__() # Initialize the Sprite base class
        self.x, self.y = pos
        self.damage = damage
        self.speed = speed
        self.is_dead = False

        if image_surface:
            self.image = image_surface
        else:
            try:
                self.image = pygame.image.load(self.IMAGE_PATH).convert_alpha()
            except pygame.error as e: # More specific exception
                print(f"Failed to load projectile image '{self.IMAGE_PATH}': {e}. Using fallback.")
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                self.image.fill((255, 255, 0, 180)) # Semi-transparent yellow
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, enemies):
        if self.is_dead or not self.alive(): # Check if sprite is alive
            return
        self.x += self.speed # Use instance specific speed
        self.rect.centerx = int(self.x)
        # 碰撞檢查
        for enemy in enemies:
            # Ensure enemy is alive and projectile collides
            if hasattr(enemy, 'hp') and enemy.hp > 0 and self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.is_dead = True
                self.kill() # Remove from sprite groups if any
                break
        # 超出畫面自動消失
        if self.x > 1000:  # 假設畫面寬度最大 1000
            self.is_dead = True
            self.kill()

    def draw(self, screen):
        if not self.is_dead:
            screen.blit(self.image, self.rect)

    def kill(self):
        """Marks the projectile as dead and removes it from sprite groups."""
        self.is_dead = True
        super().kill() # Call the parent Sprite's kill method


class FrozenProjectile(Projectile):
    """
    A projectile that damages and slows enemies.
    """
    # Fallback image path if no surface is provided
    FALLBACK_IMAGE_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "frozen_pea.png")

    def __init__(self, pos, damage=20, speed=Projectile.DEFAULT_SPEED,
                 slow_duration=2.0, slow_factor=0.5, image_surface=None):
        """
        Initializes a FrozenProjectile.
        Args:
            pos (tuple): (x, y) initial position.
            damage (int): Damage dealt to the enemy.
            speed (int): Speed of the projectile.
            slow_duration (float): Duration of the slow effect in seconds.
            slow_factor (float): Factor by which enemy speed is multiplied.
            image_surface (pygame.Surface, optional): Pre-loaded image for the projectile.
        """
        # super().__init__() is called by Projectile's __init__
        # No need to call pygame.sprite.Sprite.__init__() here again
        super().__init__(pos, damage, speed, image_surface)
        self.slow_duration = slow_duration
        self.slow_factor = slow_factor

        if not image_surface: # If no surface provided, try loading fallback
            try:
                self.image = pygame.image.load(FrozenProjectile.FALLBACK_IMAGE_PATH).convert_alpha()
            except pygame.error as e:
                print(f"Failed to load frozen projectile image '{FrozenProjectile.FALLBACK_IMAGE_PATH}': {e}. Using Projectile's fallback.")
                # Fallback is handled by super if self.image is still None or if super() used its own fallback
                if self.image is None or self.image.get_size() == (20,20): # Check if super used its basic fallback
                    fallback_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(fallback_surface, (173, 216, 230, 180), (10, 10), 10) # Semi-transparent Light blue
                    self.image = fallback_surface
            self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, enemies):
        """
        Updates the frozen projectile's position and handles collision with enemies.
        Applies a slow effect upon hitting an enemy.
        """
        super().update(enemies) # Handles movement and basic collision
        if self.is_dead: # Check if super().update() marked it as dead (due to collision)
            # Find which enemy was hit (this is a bit redundant if super().update() already did it)
            for enemy in enemies:
                if hasattr(enemy, 'hp') and enemy.hp > 0 and self.rect.colliderect(enemy.rect): # Re-check collision for effect
                    if hasattr(enemy, 'apply_slow'):
                        enemy.apply_slow(self.slow_duration, self.slow_factor)
                    break # Apply to first hit enemy


class FireProjectile(Projectile):
    """
    A projectile that deals fire damage (currently standard damage).
    Visuals are different.
    """
    # Fallback image path if no surface is provided
    FALLBACK_IMAGE_PATH = os.path.join(PROJECT_ROOT, "assets", "images", "fire_pea_placeholder.png") # Create a placeholder if needed

    def __init__(self, pos, damage=20, speed=Projectile.DEFAULT_SPEED, image_surface=None):
        # super().__init__() is called by Projectile's __init__
        # No need to call pygame.sprite.Sprite.__init__() here again
        super().__init__(pos, damage, speed, image_surface)
        # Specific fire properties can be added here if any
        if not image_surface: # If no surface provided, try loading fallback
            try:
                self.image = pygame.image.load(FireProjectile.FALLBACK_IMAGE_PATH).convert_alpha()
            except pygame.error as e:
                print(f"Failed to load fire projectile image '{FireProjectile.FALLBACK_IMAGE_PATH}': {e}. Using Projectile's fallback.")
                if self.image is None or self.image.get_size() == (20,20):
                    fallback_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(fallback_surface, (255, 100, 0, 180), (10, 10), 10) # Semi-transparent Orange
                    self.image = fallback_surface
            self.rect = self.image.get_rect(center=(self.x, self.y))