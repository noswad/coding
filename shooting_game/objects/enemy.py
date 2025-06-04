import pygame
import random
import math # Added: For math functions like pi, cos, sin, atan2, hypot
from settings import *
from resources import *
from objects.particle import AfterImage # Added: For EliteEnemy afterimages

# Constants for animation and effects
ENEMY_ANIM_SPEED = 0.1
ELITE_ENEMY_ANIM_SPEED = 0.12
BOSS_INTRO_FLASH_CYCLE_MS = 300  # Total cycle duration for boss intro flash
BOSS_INTRO_FLASH_ON_MS = 150     # Duration the flash is "on" during the cycle

class Enemy:
    def __init__(self, x_ratio, y_ratio): # x_ratio, y_ratio are fractions of WIDTH/HEIGHT
        self.width = int(WIDTH * ENEMY_SIZE_RATIO[0])
        self.height = int(HEIGHT * ENEMY_SIZE_RATIO[1])
        self.x = WIDTH * x_ratio
        self.y = HEIGHT * y_ratio
        self.speed_ratio = 0.00125 # 1 for WIDTH 800
        self.speed = WIDTH * self.speed_ratio
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.diving = False; self.dive_angle = 0
        self.dive_speed_ratio_min = 0.005   # 4.0 for WIDTH 800
        self.dive_speed_ratio_max = 0.00875 # 7.0 for WIDTH 800
        self.dive_speed = 0
        self.original_x = self.x; self.original_y = self.y
        self.frame = random.uniform(0, 2 * math.pi) # Use math.pi and random.uniform
        self.is_flashing = False
        self.flash_duration_frames = int(FPS * 0.0667) # 4 frames at 60 FPS
        self.flash_timer = 0
        self.flash_color = (220, 220, 220); self.can_shoot = True
        self.is_in_boss_intro_phase = False; self.score_value = 10
        self.is_escort = False
        self.vertical_spacing_ratio = 0.0333 # 20 for HEIGHT 600

    def draw(self, surface): # Accept surface as an argument
        if enemy_img: # Check if enemy_img itself is loaded
            self.frame += ENEMY_ANIM_SPEED; scale = 1.0 + 0.1 * pygame.math.sin(self.frame)
            w = int(self.width * scale); h = int(self.height * scale)
            current_scaled_img = pygame.transform.scale(enemy_img, (w, h))
            draw_x = self.x + (self.width - w) // 2; draw_y = self.y + (self.height - h) // 2
            if self.is_flashing:
                current_scaled_img.fill(self.flash_color, special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(current_scaled_img, (draw_x, draw_y)) # Use surface
        else:
            base_color = YELLOW if self.diving else RED
            pygame.draw.rect(surface, base_color, self.rect) # Use surface
            if self.is_flashing:
                flash_surface = pygame.Surface(self.rect.size); flash_surface.fill(self.flash_color)
                surface.blit(flash_surface, self.rect.topleft, special_flags=pygame.BLEND_RGB_ADD) # Use surface    def move(self):
        if self.is_escort: return
        if not self.diving:
            self.x += self.speed
            if self.x <= 0 or self.x >= WIDTH - self.width:
                self.speed = -self.speed; self.y += HEIGHT * self.vertical_spacing_ratio
        else:
            self.x += math.cos(self.dive_angle) * self.dive_speed
            self.y += math.sin(self.dive_angle) * self.dive_speed
            if self.y > HEIGHT or self.x < -self.width or self.x > WIDTH: # Adjusted boundary
                self.diving = False; self.x = self.original_x; self.y = self.original_y
        self.rect.x = self.x; self.rect.y = self.y
    def start_dive(self, target_x, target_y):
        self.diving = True; self.original_x = self.x; self.original_y = self.y
        dx = target_x - self.x; dy = target_y - self.y
        self.dive_angle = math.atan2(dy, dx)
        self.dive_speed = random.uniform(WIDTH * self.dive_speed_ratio_min, WIDTH * self.dive_speed_ratio_max)
    def hit_flash(self): self.is_flashing = True; self.flash_timer = self.flash_duration_frames
    def update(self):
        if self.is_flashing:
            self.flash_timer -= 1
            if self.flash_timer <= 0: self.is_flashing = False
        if self.is_in_boss_intro_phase:
            self.can_shoot = False # Ensure enemy cannot shoot during boss intro
            if (pygame.time.get_ticks() % BOSS_INTRO_FLASH_CYCLE_MS) < BOSS_INTRO_FLASH_ON_MS:
                self.is_flashing = True # Override normal flash state if condition met

class EliteEnemy(Enemy):
    def __init__(self, x_ratio, y_ratio):
        super().__init__(x_ratio, y_ratio); self.health = 2
        self.image = elite_enemy_img
        if self.image:
            self.width = self.image.get_width(); self.height = self.image.get_height()
        else: # Fallback if image not loaded, use ratios
            self.width = int(WIDTH * ELITE_ENEMY_SIZE_RATIO[0])
            self.height = int(HEIGHT * ELITE_ENEMY_SIZE_RATIO[1])
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) # Update rect with new size
        self.base_dive_speed_min_ratio = 0.0075  # 6.0 for WIDTH 800
        self.base_dive_speed_max_ratio = 0.01125 # 9.0 for WIDTH 800
        self.afterimages = []
        self.afterimage_interval_frames = int(FPS * 0.0667) # 4 frames at 60 FPS
        self.afterimage_timer = 0
        self.score_value = 25; self.swoop_amplitude = 0
        self.MAX_AFTERIMAGES = 7 # Maximum number of afterimages
        self.swoop_frequency_rad_per_frame = 0; self.swoop_direction = 1
        self.dive_progress_timer = 0
    def start_dive(self, target_x, target_y):
        super().start_dive(target_x, target_y) # Calls parent's start_dive
        # Override dive_speed with Elite's ratios
        self.dive_speed = random.uniform(WIDTH * self.base_dive_speed_min_ratio, WIDTH * self.base_dive_speed_max_ratio)
        self.afterimages.clear(); self.afterimage_timer = 0; self.dive_progress_timer = 0
        self.swoop_direction = random.choice([-1, 1])
        self.swoop_amplitude = self.dive_speed * random.uniform(1.0, 2.0)
        dist_to_target = math.hypot(target_x - self.x, target_y - self.y) if self.dive_speed > 0 else float('inf')
        self.estimated_dive_frames = max(int(FPS*0.5), dist_to_target / self.dive_speed) if self.dive_speed > 0 else int(FPS*0.5) # Min 30 frames
        num_swoop_cycles = random.uniform(0.75, 1.5)
        self.swoop_frequency_rad_per_frame = (num_swoop_cycles * 2 * math.pi) / self.estimated_dive_frames if self.estimated_dive_frames > 0 else 0
    def move(self):
        if self.is_escort: return
        old_x, old_y = self.x, self.y
        if not self.diving: super().move()
        else:
            self.dive_progress_timer += 1
            main_vx = math.cos(self.dive_angle) * self.dive_speed
            main_vy = math.sin(self.dive_angle) * self.dive_speed
            swoop_velocity_magnitude = self.swoop_amplitude * self.swoop_frequency_rad_per_frame * math.cos(self.swoop_frequency_rad_per_frame * self.dive_progress_timer)
            perp_vec_x = -math.sin(self.dive_angle); perp_vec_y = math.cos(self.dive_angle)
            swoop_vx = perp_vec_x * swoop_velocity_magnitude * self.swoop_direction
            swoop_vy = perp_vec_y * swoop_velocity_magnitude * self.swoop_direction
            self.x += main_vx + swoop_vx; self.y += main_vy + swoop_vy
            self.rect.x = int(self.x); self.rect.y = int(self.y)
            self.afterimage_timer += 1
            if self.afterimage_timer >= self.afterimage_interval_frames:
                self.afterimage_timer = 0 # Reset timer
                if len(self.afterimages) < self.MAX_AFTERIMAGES:
                    img_for_afterimage = self.image if self.image else None
                    # Afterimage lifetime and fade speed also need to be relative or FPS-independent
                    self.afterimages.append(AfterImage(img_for_afterimage, old_x, old_y, lifetime_ratio=0.25, fade_speed_ratio=0.0015)) # 15 frames, 0.09
            buffer_abs = self.width * 2
            if self.y > HEIGHT + buffer_abs or self.y < -buffer_abs or self.x < -buffer_abs or self.x > WIDTH + buffer_abs or \
               (hasattr(self, 'estimated_dive_frames') and self.dive_progress_timer > self.estimated_dive_frames * 1.5) :
                self.diving = False; self.x = self.original_x; self.y = self.original_y
                self.rect.x = int(self.x); self.rect.y = int(self.y); self.afterimages.clear()
        for img in self.afterimages[:]:
            img.update()
            if not img.is_alive(): self.afterimages.remove(img)

    def set_position_around_boss(self, boss_center_x, boss_center_y, radius_abs, angle):
        self.is_escort = True
        self.x = boss_center_x + radius_abs * math.cos(angle) - self.width / 2
        self.y = boss_center_y + radius_abs * math.sin(angle) - self.height / 2
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface): # Accept surface as an argument
        for afterimage in self.afterimages: afterimage.draw(surface) # Pass surface
        if self.is_escort:
            img_to_draw = self.image if self.image else elite_enemy_img
            if img_to_draw:
                surface.blit(img_to_draw, self.rect.topleft) # Use surface
            return
        current_image_to_draw = self.image if self.image else None
        if current_image_to_draw:
            self.frame += ELITE_ENEMY_ANIM_SPEED; scale = 1.0 + 0.10 * math.sin(self.frame)
            w, h = int(self.width * scale), int(self.height * scale)
            scaled_img = pygame.transform.scale(current_image_to_draw, (w,h))
            draw_x, draw_y = self.x + (self.width - w)//2, self.y + (self.height - h)//2
            if self.is_flashing: scaled_img.fill(self.flash_color, special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(scaled_img, (draw_x, draw_y)) # Use surface
        else:
            color = (150, 0, 150) if self.diving else (200, 50, 200)
            pygame.draw.rect(surface, color, self.rect) # Use surface
            if self.is_flashing:
                flash_surface = pygame.Surface(self.rect.size); flash_surface.fill(self.flash_color)
                surface.blit(flash_surface, self.rect.topleft, special_flags=pygame.BLEND_RGB_ADD) # Use surface
    def update(self):
        super().update()
        if self.is_escort:
            return
    def take_damage(self):
        self.health -= 1; self.hit_flash(); return self.health <= 0