import pygame
import random
import math
from settings import *
from resources import *
from objects.particle import Particle

class Bullet:
    def __init__(self, x, y): # x, y are absolute positions
        self.x = x; self.y = y
        if player_bullet_img: # Check if player_bullet_img itself is loaded
            self.width = player_bullet_img.get_width(); self.height = player_bullet_img.get_height()
        else: # Fallback sizes based on ratio
            self.width = int(WIDTH * PLAYER_BULLET_SIZE_RATIO[0]) if PLAYER_BULLET_SIZE_RATIO[0] > 0 else 5
            self.height = int(HEIGHT * PLAYER_BULLET_SIZE_RATIO[1]) if PLAYER_BULLET_SIZE_RATIO[1] > 0 else 15
        self.speed_ratio = 0.01166 # 7 for HEIGHT 600
        self.speed = HEIGHT * self.speed_ratio
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.particles = []
    def draw(self, surface): # Accept surface as an argument
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive(): self.particles.remove(particle)
            else: particle.draw(surface) # Pass surface
        if player_bullet_img: surface.blit(player_bullet_img, (self.x, self.y)) # Use surface
        else: pygame.draw.rect(surface, BLUE, self.rect) # Use surface
    def move(self):
        if random.random() < 0.4:
            # Particle properties relative to bullet or screen size
            color = (100, 150, 255)
            size_ratio = random.uniform(0.0025, 0.005) # 2 to 4 for WIDTH 800
            lifetime_ratio = random.uniform(0.166, 0.333) # 10 to 20 frames
            glow = random.random() < 0.3
            self.particles.append(Particle(self.x + self.width/2 + random.uniform(-WIDTH*0.0025, WIDTH*0.0025),
                                           self.y + self.height + random.uniform(-HEIGHT*0.0016, HEIGHT*0.0016),
                                           color, speed_ratio=0.001, size_ratio=size_ratio, lifetime_ratio=lifetime_ratio, glow=glow))
        self.y -= self.speed; self.rect.y = self.y
    pass

class BossBullet:
    def __init__(self, x, y, angle_rad, speed_abs, is_homing=False, homing_strength=0.02): # speed_abs is absolute
        self.original_x = x; self.original_y = y
        self.angle_rad = angle_rad; self.speed = speed_abs # Use absolute speed
        self.is_homing = is_homing
        self.homing_strength = homing_strength
        self.dt_ms = 16

        self.image_original_clean = None
        bullet_width = int(WIDTH * BOSS_BULLET_SIZE_RATIO[0])
        bullet_height = int(HEIGHT * BOSS_BULLET_SIZE_RATIO[1])

        if boss_bullet_single_img:
            self.image_original_clean = pygame.transform.scale(boss_bullet_single_img, (bullet_width, bullet_height))
        else:
            self.image_original_clean = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
            # Polygon points should be relative to bullet_width/height
            # Example: (16,5) for 32x32 -> (bullet_width*0.5, bullet_height*0.15625)
            center_x, center_y = bullet_width / 2, bullet_height / 2
            p1 = (center_x, bullet_height * 0.15625)
            p2 = (bullet_width * 0.65625, center_y)
            p3 = (center_x, bullet_height * 0.84375)
            p4 = (bullet_width * 0.34375, center_y)
            pygame.draw.polygon(self.image_original_clean, ORANGE, [p1, p2, p3, p4])


        self.image_to_draw = self.image_original_clean.copy()
        self.rect = self.image_to_draw.get_rect(center=(int(x), int(y)))
        self.mask = pygame.mask.from_surface(self.image_to_draw)
        self.collision_rect_for_fallback = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height * 0.5)

        self.rotation_angle_deg = 0
        self.rotation_speed_dps = 180 # Degrees per second
        self.is_flashing_effect = True
        self.flash_timer_ms = 0; self.flash_interval_ms = 150
        self.flash_alpha = 255
        self.vx = math.cos(angle_rad) * self.speed
        self.vy = math.sin(angle_rad) * self.speed
        self.trail_particles = []
        self.trail_spawn_timer_frames = 0
        self.trail_spawn_interval_frames = int(FPS * 0.0333) # 2 frames at 60 FPS

    def _rotate_and_flash(self):
        self.rotation_angle_deg = (self.rotation_angle_deg + self.rotation_speed_dps * (self.dt_ms/1000.0)) % 360
        rotated_image = pygame.transform.rotate(self.image_original_clean, -self.rotation_angle_deg)
        if self.is_flashing_effect:
            now_ms = pygame.time.get_ticks()
            if now_ms - self.flash_timer_ms > self.flash_interval_ms:
                self.flash_timer_ms = now_ms
                self.flash_alpha = 150 if self.flash_alpha == 255 else 255
            final_image = rotated_image.copy()
            final_image.set_alpha(self.flash_alpha)
            self.image_to_draw = final_image
        else:
            self.image_to_draw = rotated_image
        current_center = self.rect.center
        self.rect = self.image_to_draw.get_rect(center=current_center)
        self.mask = pygame.mask.from_surface(self.image_to_draw)
        self.collision_rect_for_fallback.center = self.rect.center

    def _update_homing(self, player_rect, dt_ms_val):
        if not player_rect or not self.is_homing: return
        target_x, target_y = player_rect.center
        dx = target_x - self.original_x
        dy = target_y - self.original_y
        if dx == 0 and dy == 0: return
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - self.angle_rad
        while angle_diff > math.pi: angle_diff -= 2 * math.pi
        while angle_diff < -math.pi: angle_diff += 2 * math.pi
        max_turn_this_frame = self.homing_strength * (math.pi * 2) * (dt_ms_val/1000.0)
        turn_amount = max(-max_turn_this_frame, min(max_turn_this_frame, angle_diff * self.homing_strength))
        self.angle_rad += turn_amount
        self.vx = math.cos(self.angle_rad) * self.speed
        self.vy = math.sin(self.angle_rad) * self.speed

    def update(self, player_rect=None, dt_ms_val=16):
        self.dt_ms = dt_ms_val
        self._rotate_and_flash()
        if self.is_homing and player_rect:
            self._update_homing(player_rect, dt_ms_val)
        self.original_x += self.vx * (dt_ms_val / (1000/FPS)) # Scale movement by dt
        self.original_y += self.vy * (dt_ms_val / (1000/FPS))
        self.rect.center = (int(self.original_x), int(self.original_y))
        self.collision_rect_for_fallback.center = self.rect.center
        self.trail_spawn_timer_frames += 1
        if self.trail_spawn_timer_frames >= self.trail_spawn_interval_frames:
            self.trail_spawn_timer_frames = 0
            if self.image_original_clean:
                trail_color = (255, 200, 100, 150)
                p_x = self.rect.centerx + random.uniform(-WIDTH*0.0025, WIDTH*0.0025)
                p_y = self.rect.centery + random.uniform(-WIDTH*0.0025, WIDTH*0.0025)
                self.trail_particles.append(Particle(p_x, p_y, trail_color, speed_ratio=0.00025, # 0.2
                                                      size_ratio=random.uniform(0.00375,0.00625), # 3 to 5
                                                      lifetime_ratio=0.166, glow=False)) # 10 frames
        for p in self.trail_particles[:]:
            p.update()
            if not p.is_alive(): self.trail_particles.remove(p)
        if not screen.get_rect().colliderect(self.rect):
            return False
        return True

    def draw(self, surface):
        for p in self.trail_particles: p.draw(surface)
        if self.image_to_draw:
            current_pos = self.rect.topleft
            surface.blit(self.image_to_draw, current_pos)
        else:
            pygame.draw.circle(surface, ORANGE, self.rect.center, int(WIDTH * 0.0125)) # 10
    pass

class ScatterBullet:
    def __init__(self, x, y, angle_rad, speed_abs, size_ratio_base=0.0075, lifetime_sec=2.5, color=ORANGE): # speed_abs, size_ratio_base=6
        self.x = x
        self.y = y
        self.vx = math.cos(angle_rad) * speed_abs
        self.vy = math.sin(angle_rad) * speed_abs
        self.size_abs = random.uniform(WIDTH * size_ratio_base * 0.7, WIDTH * size_ratio_base * 1.3)
        self.lifetime_frames = int(FPS * lifetime_sec)
        self.color = color
        self.image_original = pygame.Surface((int(self.size_abs*2), int(self.size_abs*2)), pygame.SRCALPHA)
        pygame.draw.circle(self.image_original, self.color, (int(self.size_abs), int(self.size_abs)), int(max(1,self.size_abs)))
        pygame.draw.circle(self.image_original, BLACK, (int(self.size_abs), int(self.size_abs)), int(max(1,self.size_abs)), 1)
        self.image_to_draw = self.image_original
        self.rect = self.image_to_draw.get_rect(center=(x,y))
        self.alpha = 255
        self.fade_per_frame = 255 / self.lifetime_frames if self.lifetime_frames > 0 else 255

    def update(self, dt_ms_val=16):
        time_scale = dt_ms_val / (1000/FPS)
        self.x += self.vx * time_scale
        self.y += self.vy * time_scale
        self.rect.center = (int(self.x), int(self.y))
        self.lifetime_frames -= 1
        self.alpha -= self.fade_per_frame
        if self.alpha < 0: self.alpha = 0
        if self.lifetime_frames <= 0 or not screen.get_rect().colliderect(self.rect) or self.alpha <= 0:
            return False # screen.get_rect() is okay here for boundary check
        return True

    def draw(self, surface):
        if self.alpha > 0 and self.size_abs > 0:
            temp_image = self.image_to_draw.copy()
            temp_image.set_alpha(int(self.alpha))
            surface.blit(temp_image, self.rect.topleft)
    pass

class EnemyBullet:
    def __init__(self, x, y): # x, y are absolute
        self.x = x; self.y = y
        if cocoa_bullet_img: # Check if cocoa_bullet_img itself is loaded
            self.width = cocoa_bullet_img.get_width(); self.height = cocoa_bullet_img.get_height()
        else: # Fallback sizes based on ratio
            self.width = int(WIDTH * COCOA_BULLET_SIZE_RATIO[0]) if COCOA_BULLET_SIZE_RATIO[0] > 0 else 5
            self.height = int(HEIGHT * COCOA_BULLET_SIZE_RATIO[1]) if COCOA_BULLET_SIZE_RATIO[1] > 0 else 10
        self.speed_ratio = 0.00833 # 5 for HEIGHT 600
        self.speed = HEIGHT * self.speed_ratio
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.particles = []
    def draw(self, surface): # Accept surface as an argument
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive(): self.particles.remove(particle)
            else: particle.draw(surface) # Pass surface
        if cocoa_bullet_img: surface.blit(cocoa_bullet_img, (self.x, self.y)) # Use surface
        else: pygame.draw.rect(surface, PURPLE, self.rect) # Use surface
    def move(self):
        if random.random() < 0.4:
            color = (200, 100, 255)
            size_ratio = random.uniform(0.0025, 0.005) # 2 to 4
            lifetime_ratio = random.uniform(0.166, 0.333) # 10 to 20 frames
            glow = random.random() < 0.3
            self.particles.append(Particle(self.x + self.width/2 + random.uniform(-WIDTH*0.0025, WIDTH*0.0025),
                                           self.y + random.uniform(-HEIGHT*0.0016, HEIGHT*0.0016),
                                           color, speed_ratio=0.001, size_ratio=size_ratio, lifetime_ratio=lifetime_ratio, glow=glow))
        self.y += self.speed; self.rect.y = self.y
    pass