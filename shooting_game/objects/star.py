import pygame
import random
from settings import WIDTH, HEIGHT

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size_ratio = random.uniform(0.00125, 0.00375)
        self.size = int(max(1, WIDTH * self.size_ratio))
        self.speed_ratio = random.uniform(0.000166, 0.000833)
        self.speed = HEIGHT * self.speed_ratio
        self.color = (
            random.randint(180, 255),
            random.randint(180, 255),
            random.randint(180, 255)
        )

    def update_position(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface): # Accept surface as an argument
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size) # Use surface