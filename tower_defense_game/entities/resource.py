# d:\coding\tower_defense_game\entities\resource.py
import pygame
import os

# Determine the project root directory (d:/coding/tower_defense_game)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Sun(pygame.sprite.Sprite): # Inherit from pygame.sprite.Sprite
    IMAGE_FILENAME = "sun.png"  # Example image file name
    DEFAULT_VALUE = 25          # Default sun value
    FALLING_SPEED = 2           # Pixels per frame

    def __init__(self, initial_pos, target_pos, value=DEFAULT_VALUE, image=None):
        """
        Initializes a Sun resource.

        Args:
            initial_pos (tuple): (x, y) The starting position of the sun.
            target_pos (tuple): (x, y) The position where the sun should fall to.
            value (int): The resource value this sun provides when collected.
            image (pygame.Surface or None): Optional. If provided, use this as the sun's image.
        """
        super().__init__() # Initialize the Sprite base class
        self.x, self.y = initial_pos
        self.target_x, self.target_y = target_pos
        self.value = value
        self.is_dead = False  # Becomes True when collected or disappears

        if image is not None:
            self.image = image
        else:
            self.image_path = os.path.join(PROJECT_ROOT, "assets", "images", Sun.IMAGE_FILENAME)
            try:
                self.image = pygame.image.load(self.image_path).convert_alpha()
            except Exception as e:
                print(f"[WARNING] Failed to load sun image: {e}, using fallback.")
                self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 223, 0), (24, 24), 24)
        
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        """
        Updates the sun's position (e.g., falling animation).
        """
        if self.is_dead:
            return

        # Simple falling logic towards the target y-coordinate
        if self.y < self.target_y:
            self.y += Sun.FALLING_SPEED
            if self.y > self.target_y: # Overshot
                self.y = self.target_y
        
        # Update rect position
        self.rect.centery = int(self.y)
        self.rect.centerx = int(self.x) # Assuming x doesn't change during fall for now

    def draw(self, screen):
        """
        Draws the sun on the given screen.
        """
        if not self.is_dead:
            screen.blit(self.image, self.rect)

    def collect(self):
        if not self.is_dead:
            self.is_dead = True
            # self.kill() # The ResourceManager will call kill() after successful collection
            return self.value
        return 0