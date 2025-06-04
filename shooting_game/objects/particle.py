import pygame
import random
import math
from settings import *
from resources import *

class AfterImage:
    def __init__(self, image, x, y, lifetime_ratio=0.25, fade_speed_ratio=0.00116): # lifetime=15/60, fade_speed=0.07
        self.image = image
        self.x = x
        self.y = y
        self.lifetime = int(FPS * lifetime_ratio)
        self.fade_speed = fade_speed_ratio * FPS # 0.07
        self.alpha = 200
        if image: self.surface = image.copy()
        else:
            # Fallback surface size based on player size ratio
            fallback_width = int(WIDTH * PLAYER_SIZE_RATIO[0])
            fallback_height = int(HEIGHT * PLAYER_SIZE_RATIO[1])
            self.surface = pygame.Surface((fallback_width, fallback_height), pygame.SRCALPHA)
            pygame.draw.rect(self.surface, (0, 255, 0, 200), (0, 0, fallback_width, fallback_height))
    def update(self):
        self.alpha -= self.fade_speed * (255 / FPS) # Scale fade speed by FPS
        self.lifetime -= 1
    def draw(self, surface):
        if self.alpha > 0:
            self.surface.set_alpha(int(self.alpha))
            surface.blit(self.surface, (self.x, self.y))
    def is_alive(self): return self.lifetime > 0
    pass

class Particle:
    def __init__(self, x, y, color, speed_ratio=0.00125, size_ratio=0.00375, lifetime_ratio=0.5, glow=False): # speed=1, size=3, lifetime=30
        self.x = x; self.y = y; self.color = color
        self.base_size = int(max(1, WIDTH * size_ratio)) # Ensure size is at least 1
        self.size = random.randint(1, self.base_size)
        self.lifetime = int(FPS * lifetime_ratio)
        self.original_lifetime = self.lifetime; self.current_size = self.size
        self.glow = glow
        angle = random.uniform(0, 2 * math.pi)
        eff_speed = random.uniform(0.5 * (WIDTH * speed_ratio), (WIDTH * speed_ratio))
        self.vx = math.cos(angle) * eff_speed
        self.vy = math.sin(angle) * eff_speed
        self.base_color = color
        if isinstance(color, tuple) and len(color) >= 3:
            self.color_shift = (random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20))
        else: self.color_shift = (0, 0, 0)
        self.current_color = self.base_color
    def update(self):
        self.x += self.vx; self.y += self.vy; self.lifetime -= 1
        self.vx *= 0.98; self.vy *= 0.98 # Deceleration
        if self.original_lifetime > 0:
            ratio = self.lifetime / self.original_lifetime
            self.current_size = self.size * ratio
            if isinstance(self.base_color, tuple) and len(self.base_color) >= 3:
                r = max(0, min(255, self.base_color[0] + self.color_shift[0] * ratio))
                g = max(0, min(255, self.base_color[1] + self.color_shift[1] * ratio))
                b = max(0, min(255, self.base_color[2] + self.color_shift[2] * ratio))
                self.current_color = (int(r), int(g), int(b))
            else: self.current_color = self.base_color
        else:
            self.current_size = 0 # Instantly dead if original_lifetime is 0
    def draw(self, surface):
        if self.current_size <= 0: return
        pygame.draw.circle(surface, self.current_color, (int(self.x), int(self.y)), int(max(1, self.current_size))) # Ensure radius is at least 1
        if self.glow and self.current_size > 1.5 * (WIDTH * 0.00125): # Glow if size > 1.5 pixels
            glow_size_abs = self.current_size * 1.5
            glow_surface = pygame.Surface((int(glow_size_abs*2), int(glow_size_abs*2)), pygame.SRCALPHA)
            if self.original_lifetime > 0:
                for i in range(3):
                    alpha = 100 * (1 - i/3) * (self.lifetime / self.original_lifetime)
                    size_abs = glow_size_abs * (1 - i/5)
                    glow_c = (self.current_color[0], self.current_color[1], self.current_color[2], int(alpha)) if isinstance(self.current_color, tuple) and len(self.current_color) >=3 else (255,255,255, int(alpha))
                    pygame.draw.circle(glow_surface, glow_c, (int(glow_size_abs), int(glow_size_abs)), int(max(1,size_abs)))
                surface.blit(glow_surface, (int(self.x-glow_size_abs), int(self.y-glow_size_abs)))
    def is_alive(self): return self.lifetime > 0
    pass

class Explosion:
    def __init__(self, x, y, size_multiplier=1.0, particle_count_base=40):
        self.id = id(self) # For debugging
        # print(f"DEBUG: Explosion {self.id} created at ({x:.2f},{y:.2f})") # Optional: uncomment for creation log
        self.x = x; self.y = y; self.particles = []; self.lifetime = 0
        self.rings = []; self.ring_timer = 0
        colors = [(255, 100, 0), (255, 160, 0), (255, 220, 0), (255, 255, 255)]
        particle_count = int(particle_count_base * size_multiplier)
        for _ in range(particle_count):
            color = random.choice(colors)
            # Particle speed and size now relative to WIDTH
            speed_ratio = random.uniform(0.00125, 0.005) * size_multiplier # 1.0 to 4.0 for WIDTH 800
            particle_size_ratio = random.uniform(0.0025, 0.0075) # 2 to 6 for WIDTH 800
            lifetime_ratio = random.uniform(0.33, 1.0) # 20 to 60 frames
            glow = random.random() < 0.3
            self.particles.append(Particle(x, y, color, speed_ratio, particle_size_ratio, lifetime_ratio, glow))

        flash_size_base = WIDTH * 0.025 # 20 for WIDTH 800
        self.flash = {'size': flash_size_base * size_multiplier, 'alpha': 200, 'color': (255, 255, 255)}
        self.ring_max_radius_base = WIDTH * 0.05 # 40 for WIDTH 800
        self.ring_width_min_ratio = 0.0025 # 2 for WIDTH 800
        self.ring_width_max_ratio = 0.005  # 4 for WIDTH 800

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive(): self.particles.remove(particle)
        if self.flash['alpha'] > 0:
            self.flash['alpha'] -= 10 * (FPS / 60) # Scale alpha fade by FPS
            self.flash['size'] *= 0.9

        # Determine if new rings should be spawned
        can_spawn_new_rings = True
        if len(self.particles) == 0 and self.flash['alpha'] <= 0:
            can_spawn_new_rings = False # Stop spawning if main particle/flash effects are done

        self.ring_timer += 1
        if can_spawn_new_rings and self.ring_timer >= 2 * (60 / FPS) and len(self.rings) < 3: # Scale ring spawn by FPS
            ring_width = random.randint(int(WIDTH * self.ring_width_min_ratio), int(WIDTH * self.ring_width_max_ratio))
            self.rings.append({'radius': WIDTH * 0.00625, 'max_radius': self.ring_max_radius_base + random.randint(0, int(WIDTH*0.025)),
                               'width': ring_width, 'color': (255, 200, 50), 'alpha': 180})
            self.ring_timer = 0
        for ring in self.rings[:]:
            # # DEBUG print statements for ring properties
            # # print(f"DEBUG: Explosion {self.id} - Ring (ID: {id(ring)}) - BEFORE update: radius={ring['radius']:.2f}, alpha={ring['alpha']:.2f}, max_radius={ring['max_radius']:.2f}")
            ring['radius'] += 2 * (WIDTH / 800) # Scale radius increase
            ring['alpha'] -= 3 * (FPS / 60)     # Scale alpha fade
            # # print(f"DEBUG: Explosion {self.id} - Ring (ID: {id(ring)}) - AFTER update: radius={ring['radius']:.2f}, alpha={ring['alpha']:.2f}")
            
            if ring['alpha'] <= 0 or ring['radius'] >= ring['max_radius']:
                radius_cond_met = ring['radius'] >= ring['max_radius']
                alpha_cond_met = ring['alpha'] <= 0
                # # print(f"DEBUG: Explosion {self.id} - Ring (ID: {id(ring)}) - REMOVING. Radius cond: {radius_cond_met}, Alpha cond: {alpha_cond_met}")
                self.rings.remove(ring)
            # # else:
                # # print(f"DEBUG: Explosion {self.id} - Ring (ID: {id(ring)}) - KEEPING.")
    def draw(self, surface):
        for ring in self.rings:
            if ring['radius'] <=0 or ring['width'] <=0: continue
            ring_surface = pygame.Surface((int(ring['radius']*2), int(ring['radius']*2)), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (*ring['color'], int(max(0,ring['alpha']))),
                              (int(ring['radius']), int(ring['radius'])), int(ring['radius']), int(ring['width']))
            surface.blit(ring_surface, (self.x - ring['radius'], self.y - ring['radius']))
        if self.flash['alpha'] > 0 and self.flash['size'] > 1:
            flash_surface = pygame.Surface((int(self.flash['size']*2), int(self.flash['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*self.flash['color'], int(max(0,self.flash['alpha']))),
                              (int(self.flash['size']), int(self.flash['size'])), int(self.flash['size']))
            surface.blit(flash_surface, (self.x - self.flash['size'], self.y - self.flash['size']))
        for particle in self.particles: particle.draw(surface)
    def is_finished(self):
        finished = len(self.particles) == 0 and len(self.rings) == 0 and self.flash['alpha'] <= 0
        # if finished:
            # print(f"DEBUG: Explosion {self.id} IS_FINISHED: Particles: {len(self.particles)}, Rings: {len(self.rings)}, Flash Alpha: {(f'{self.flash["alpha"]:.2f}' if self.flash else 'N/A')}")
        # elif len(self.rings) > 0 or len(self.particles) > 0 or (self.flash and self.flash['alpha'] > 0) : # More comprehensive "not finished" log
            # print(f"DEBUG: Explosion {self.id} NOT_FINISHED: Particles: {len(self.particles)}, Rings: {len(self.rings)}, Flash Alpha: {(f'{self.flash["alpha"]:.2f}' if self.flash else 'N/A')}")
        return finished
    pass

class BloodParticle:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.base_colors = [(200, 0, 0), (150, 0, 0), (255, 50, 50), (180, 20, 20)]
        self.color = random.choice(self.base_colors)
        self.size = random.uniform(WIDTH * 0.001875, WIDTH * 0.005) # 1.5 to 4 for WIDTH 800
        self.lifetime = random.randint(FPS * 1, int(FPS * 2.5))
        angle_spread = math.pi / 2
        angle = random.uniform(-angle_spread, angle_spread) - math.pi / 2
        initial_speed_ratio = random.uniform(0.0025, 0.0075) # 2 to 6 for WIDTH 800
        initial_speed = WIDTH * initial_speed_ratio
        self.vx = math.cos(angle) * initial_speed
        self.vy = math.sin(angle) * initial_speed
        self.gravity = HEIGHT * 0.000333 # 0.2 for HEIGHT 600
    def update(self):
        self.vy += self.gravity; self.x += self.vx; self.y += self.vy; self.lifetime -= 1
        if self.lifetime % 10 == 0 and self.lifetime > 20:
            r, g, b = self.color
            self.color = (max(0, r - 5), max(0, g - 1), max(0, b - 1))
    def draw(self, surface):
        if self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(max(1, self.size)))
    def is_alive(self): return self.lifetime > 0 and self.y < HEIGHT + (HEIGHT * 0.0833) # HEIGHT + 50
    pass

class SparkParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.colors = [RED, ORANGE, YELLOW, (255,200,100), WHITE]
        self.color = random.choice(self.colors)

        self.angle = random.uniform(0, 2 * math.pi)
        self.speed_ratio = random.uniform(0.003125, 0.0075) # 2.5 to 6.0 for WIDTH 800
        self.speed = WIDTH * self.speed_ratio
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.size_ratio = random.uniform(0.001875, 0.005) # 1.5 to 4.0 for WIDTH 800
        self.size = WIDTH * self.size_ratio
        self.lifetime = random.randint(int(FPS * 0.133), int(FPS * 0.333)) # 8 to 20 frames
        self.original_lifetime = self.lifetime
        self.alpha = 255
        self.deceleration = 0.92

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.deceleration
        self.vy *= self.deceleration
        self.lifetime -= 1
        if self.lifetime <= 0 or self.original_lifetime == 0:
            self.alpha = 0
        else:
            self.alpha = int(255 * (self.lifetime / self.original_lifetime))

    def draw(self, surface):
        if self.alpha > 0 and self.size > 0.5 * (WIDTH * 0.00125): # size > 0.5 pixels
            draw_size = int(max(1, self.size))
            final_color = self.color
            if len(self.color) == 3:
                final_color = (*self.color, int(self.alpha))
            elif len(self.color) == 4:
                final_color = (*self.color[:3], int(self.alpha * (self.color[3]/255.0)))

            temp_surf = pygame.Surface((draw_size * 2, draw_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, final_color, (draw_size, draw_size), draw_size)
            surface.blit(temp_surf, (int(self.x - draw_size), int(self.y - draw_size)))

    def is_alive(self):
        return self.lifetime > 0 and self.alpha > 0
    pass

class PixelFragmentParticle:
    def __init__(self, x, y, initial_direction_angle, color=None):
        self.x = x
        self.y = y
        self.size_ratio = random.uniform(0.0025, 0.00625) # 2 to 5 for WIDTH 800
        self.size = WIDTH * self.size_ratio

        self.base_colors = [WHITE, (200,200,200), (180,180,180), (220,50,50)]
        self.color = color if color else random.choice(self.base_colors)

        self.angle = initial_direction_angle + random.uniform(-math.pi / 4, math.pi / 4)
        self.speed_ratio = random.uniform(0.001875, 0.005) # 1.5 to 4.0 for WIDTH 800
        self.speed = WIDTH * self.speed_ratio
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed

        self.lifetime = random.randint(int(FPS * 0.6), int(FPS * 1.8))
        self.original_lifetime = self.lifetime
        self.alpha = 255
        self.deceleration = 0.985
        self.bounce_dampening = 0.65

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.deceleration
        self.vy *= self.deceleration

        bounce_occurred = False
        if self.x - self.size / 2 < 0:
            self.vx = abs(self.vx) * self.bounce_dampening
            self.x = self.size / 2
            bounce_occurred = True
        elif self.x + self.size / 2 > WIDTH:
            self.vx = -abs(self.vx) * self.bounce_dampening
            self.x = WIDTH - self.size / 2
            bounce_occurred = True

        if self.y - self.size / 2 < 0:
            self.vy = abs(self.vy) * self.bounce_dampening
            self.y = self.size / 2
            bounce_occurred = True
        elif self.y + self.size / 2 > HEIGHT:
            self.vy = -abs(self.vy) * self.bounce_dampening
            self.y = HEIGHT - self.size / 2
            bounce_occurred = True

        if bounce_occurred:
            self.angle += random.uniform(-0.2, 0.2)
            current_speed_val = math.hypot(self.vx, self.vy)
            self.vx = math.cos(self.angle) * current_speed_val
            self.vy = math.sin(self.angle) * current_speed_val

        self.lifetime -= 1
        if self.lifetime <= 0 or self.original_lifetime == 0:
            self.alpha = 0
        else:
            self.alpha = int(255 * (self.lifetime / self.original_lifetime))
            if self.lifetime % 15 == 0 and isinstance(self.color, tuple) and len(self.color) == 3:
                r, g, b = self.color
                self.color = (max(0, r - 15), max(0, g - 15), max(0, b - 15))

    def draw(self, surface):
        if self.alpha > 0 and self.size > 0:
            draw_size = int(max(1, self.size))
            rect_pos_x = int(self.x - draw_size / 2)
            rect_pos_y = int(self.y - draw_size / 2)

            temp_surf = pygame.Surface((draw_size, draw_size), pygame.SRCALPHA)
            rgb_color = self.color[:3] if len(self.color) == 4 else self.color
            temp_surf.fill((*rgb_color, int(self.alpha)))
            surface.blit(temp_surf, (rect_pos_x, rect_pos_y))

    def is_alive(self):
        return self.lifetime > 0 and self.alpha > 0
    pass

class BloodSprayEffect:
    def __init__(self, x, y, particle_count_base=70):
        self.particles = []
        particle_count = int(particle_count_base * (WIDTH / 800)) # Scale particle count
        for _ in range(particle_count): self.particles.append(BloodParticle(x, y))
        pygame.mixer.music.stop()
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive(): self.particles.remove(particle)
    def draw(self, surface):
        for particle in self.particles: particle.draw(surface)
    def is_finished(self): return not self.particles
    pass