import pygame
import random
import math
from settings import *
from resources import *
from objects.bullet import BossBullet, ScatterBullet
from objects.particle import Particle, SparkParticle, PixelFragmentParticle


class BossLv1:
    """
    Represents the Level 1 Boss enemy in the game.
    Manages its own movement patterns, attack phases, health, and visual representation.
    """

    def __init__(self, x_ratio, y_ratio):  # x_ratio, y_ratio are fractions of WIDTH/HEIGHT
        self.is_flashing = False; self.flash_timer = 0
        self.flash_duration_frames = int(FPS * 0.133)  # 8 frames at 60 FPS
        self.flash_color = WHITE

        # Store base and phase-specific tinted images
        self.image_base = None  # Default base image
        self.image_phase_a_tint = None  # Red tint for phase A
        self.image_phase_b_tint = None  # Orange tint for phase B
        self.image_phase_c_tint = None  # Yellow tint for phase C

        if boss_lv1_img:
            self.image_base = boss_lv1_img.copy()
            self.width = self.image_base.get_width()
            self.height = self.image_base.get_height()
            # Assign pre-loaded tinted images if they exist and base image was loaded from file
            if boss_lv1_red_img: self.image_phase_a_tint = boss_lv1_red_img.copy()
            if boss_lv1_orange_img: self.image_phase_b_tint = boss_lv1_orange_img.copy()
            if boss_lv1_yellow_img: self.image_phase_c_tint = boss_lv1_yellow_img.copy()
        else:
            # Fallback if main boss image isn't loaded
            self.width = int(WIDTH * BOSS_LV1_SIZE_RATIO[0])
            self.height = int(HEIGHT * BOSS_LV1_SIZE_RATIO[1])
            self.image_base = pygame.Surface(
                (self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.image_base, (180, 0, 0),
                             (0, 0, self.width, self.height))
            pygame.draw.circle(self.image_base, (255, 100, 0),
                               (self.width // 2, self.height // 2), self.width // 3)
            # Note: Tint images are not assigned here if base image is a fallback,
            # as the logic above ties tint assignment to boss_lv1_img being loaded.

                                                                                self.x = WIDTH * x_ratio
                                                                                self.y = HEIGHT * y_ratio
                                                                                self.rect = pygame.Rect(
                                                                                    self.x, self.y, self.width, self.height)
                                                                                self.initial_y = self.y

                                                                                self.vertical_bob_timer = random.uniform(
                                                                                    0, math.pi * 2)
                                                                                self.vertical_bob_amplitude_ratio = 0.0166  # 10 for HEIGHT 600
                                                                                self.vertical_bob_speed = 0.03

                                                                                # Scale health with width
                                                                                self.health = 300 * \
                                                                                    (WIDTH / 800)
                                                                                self.max_health = self.health
                                                                                self.base_speed_ratio = 0.001875  # 1.5 for WIDTH 800
                                                                                self.current_speed = WIDTH * self.base_speed_ratio
                                                                                self.movement_direction = 1
                                                                                self.score_value = 1000

                                                                                self.battle_state = "ENTERING"
                                                                                self.state_timer = 0
                                                                                self.is_shaking_for_windup = False

                                                                                self.PHASE_A_SHOOT_INTERVAL_SEC = 1.5
                                                                                self.PHASE_A_POST_SHOT_DELAY_SEC = 0.5
                                                                                self.PHASE_A_SALVOS_PER_ROUND = 2
                                                                                self.phase_a_salvos_done_this_round = 0

                                                                                self.PHASE_B_WINDUP_DURATION_SEC = 0.7
                                                                                self.PHASE_B_DASH_SPEED_BASE_RATIO = 0.01  # 8 for WIDTH 800
                                                                                self.current_phase_b_dash_speed = WIDTH * self.PHASE_B_DASH_SPEED_BASE_RATIO
                                                                                self.PHASE_B_SCATTER_COUNT = 4
                                                                                self.PHASE_B_SCATTER_SPEED_RATIO = 0.005  # 4 for WIDTH 800
                                                                                self.PHASE_B_DASHES_PER_CYCLE = 2
                                                                                self.phase_b_dashes_performed_this_cycle = 0
                                                                                self.phase_b_dash_target_x = 0
                                                                                self.phase_b_dash_target_y = 0
                                                                                self.is_dashing_phase_b = False
                                                                                self.PHASE_B_POST_SCATTER_COOLDOWN_SEC = 1.0

                                                                                self.PHASE_C_SHOOT_INTERVAL_SEC = 1.0
                                                                                self.PHASE_C_TOTAL_SHOTS_PER_CYCLE = 3
                                                                                self.phase_c_shots_fired_this_cycle = 0
                                                                                self.PHASE_C_HOMING_STRENGTH_BASE = 0.025
                                                                                self.current_phase_c_homing_strength = self.PHASE_C_HOMING_STRENGTH_BASE
                                                                                self.PHASE_C_BULLET_SPEED_BASE_RATIO = 0.0035  # 2.8 for WIDTH 800
                                                                                self.current_phase_c_bullet_speed = WIDTH * self.PHASE_C_BULLET_SPEED_BASE_RATIO
                                                                                self.phase_c_move_dir = 1
                                                                                self.phase_c_move_timer = 0
                                                                                self.PHASE_C_MOVE_INTERVAL_SEC = 1.5

                                                                                self.main_cycle_state = "A"
                                                                                self.target_phase = "A"
                                                                                self.transition_timer = 0
                                                                                self.transition_duration_sec = 0.5
                                                                                self.transition_particles = []

                                                                                self.is_enraged = False
                                                                                self.enrage_hp_threshold_ratio = 0.5
                                                                                self.enraged_shoot_interval_mult = 0.7
                                                                                self.enraged_dash_speed_mult = 1.25
                                                                                self.enraged_tracking_speed_mult = 1.2
                                                                                self.enraged_homing_strength_mult = 1.2

                                                                                self.escort_radius_ratio = 0.1  # 80 for WIDTH 800
                                                                                self.escort_angle_offset = 0
                                                                                self.windup_shot_timer = 0
                                                                                self.hit_spark_particles = []
                                                                                self.pixel_fragment_particles = []
                                                                                self.escort_rotation_speed = 0.02

                                                                                # Convert second-based intervals to frame-based
                                                                                self.PHASE_A_SHOOT_INTERVAL_FRAMES = int(
                                                                                    FPS * self.PHASE_A_SHOOT_INTERVAL_SEC)
                                                                                self.PHASE_A_POST_SHOT_DELAY_FRAMES = int(
                                                                                    FPS * self.PHASE_A_POST_SHOT_DELAY_SEC)
                                                                                self.PHASE_B_WINDUP_DURATION_FRAMES = int(
                                                                                    FPS * self.PHASE_B_WINDUP_DURATION_SEC)
                                                                                self.PHASE_B_POST_SCATTER_COOLDOWN_FRAMES = int(
                                                                                    FPS * self.PHASE_B_POST_SCATTER_COOLDOWN_SEC)
                                                                                self.PHASE_C_SHOOT_INTERVAL_FRAMES = int(
                                                                                    FPS * self.PHASE_C_SHOOT_INTERVAL_SEC)
                                                                                self.PHASE_C_MOVE_INTERVAL_FRAMES = int(
                                                                                    FPS * self.PHASE_C_MOVE_INTERVAL_SEC)
                                                                                self.transition_duration_frames = int(
                                                                                    FPS * self.transition_duration_sec)
                                                                                self.boundary_margin = WIDTH * 0.025  # 20 for WIDTH 800

                                                                            def _update_escorts(self, escorts_list):
                                                                                if not escorts_list: # Avoid division by zero if list is empty
                                                                                    return
                                                                                self.escort_angle_offset = (self.escort_angle_offset + self.escort_rotation_speed) % (2 * math.pi)
                                                                                angle_step = (2 * math.pi) / len(escorts_list)
                                                                                current_escort_radius = WIDTH * self.escort_radius_ratio
                                                                                for i, escort in enumerate(escorts_list):
                                                                                    angle = self.escort_angle_offset + i * angle_step
                                                                                    escort.set_position_around_boss(self.rect.centerx, self.rect.centery, current_escort_radius, angle)

    def _fire_bullet(self, boss_bullets_list, angle_rad, speed_mult=1.0, is_homing=False, homing_strength=0.02, bullet_speed_override_ratio=None):
        bullet_base_speed_ratio = 0.005 # 4 for WIDTH 800
        if is_homing:
            bullet_base_speed_abs = self.current_phase_c_bullet_speed # Already scaled
        else:
            bullet_base_speed_abs = WIDTH * bullet_base_speed_ratio

        final_speed_abs = bullet_base_speed_abs * speed_mult
        if bullet_speed_override_ratio is not None:
            final_speed_abs = WIDTH * bullet_speed_override_ratio

        spawn_x = self.rect.centerx
        spawn_y = self.rect.bottom - (HEIGHT * 0.0166) # 10 for HEIGHT 600

        boss_bullets_list.append(BossBullet(spawn_x, spawn_y, angle_rad, final_speed_abs,
                                            is_homing=is_homing, homing_strength=homing_strength if is_homing else 0))
        play_sound(boss_shoot_sound if boss_shoot_sound else None)

    def _get_aim_angle_to_player(self, player_rect):
        if not player_rect: return math.pi / 2
        target_x = player_rect.centerx
        target_y = player_rect.centery
        dx = target_x - self.rect.centerx
        dy = target_y - (self.rect.bottom - (HEIGHT * 0.0166))
        return math.atan2(dy, dx)

    def _update_enrage_status(self):
        if not self.is_enraged and self.health <= self.max_health * self.enrage_hp_threshold_ratio:
            self.is_enraged = True
            print("BOSS ENRAGED!")
            self.current_phase_b_dash_speed = (WIDTH * self.PHASE_B_DASH_SPEED_BASE_RATIO) * self.enraged_dash_speed_mult
            self.current_phase_c_bullet_speed = (WIDTH * self.PHASE_C_BULLET_SPEED_BASE_RATIO) * self.enraged_tracking_speed_mult
            self.current_phase_c_homing_strength = self.PHASE_C_HOMING_STRENGTH_BASE * self.enraged_homing_strength_mult

    def _transition_to_phase(self, next_phase_char):
        print(f"Boss 從階段 {self.main_cycle_state} 轉換到 {next_phase_char}")
        self.battle_state = "PHASE_TRANSITION"
        self.target_phase = next_phase_char
        self.state_timer = 0

    def _update_phase_a(self, boss_bullets_list, player_rect):
        if self.battle_state == "PHASE_A_SHOOT":
            actual_shoot_interval = self.PHASE_A_SHOOT_INTERVAL_FRAMES
            if self.is_enraged:
                actual_shoot_interval *= self.enraged_shoot_interval_mult
            if self.state_timer >= actual_shoot_interval:
                player_angle = self._get_aim_angle_to_player(player_rect)
                angles_deg = [0, -15, 15, -30, 30]
                for offset_deg in angles_deg:
                    self._fire_bullet(boss_bullets_list, player_angle + math.radians(offset_deg))
                self.state_timer = 0
                self.battle_state = "PHASE_A_DELAY"
        elif self.battle_state == "PHASE_A_DELAY":
            if self.state_timer >= self.PHASE_A_POST_SHOT_DELAY_FRAMES:
                self.phase_a_salvos_done_this_round += 1
                self.state_timer = 0
                if self.phase_a_salvos_done_this_round >= self.PHASE_A_SALVOS_PER_ROUND:
                    self._transition_to_phase("B")
                else:
                    self.battle_state = "PHASE_A_SHOOT"

    def _handle_standard_horizontal_movement(self):
        """Handles the boss's standard side-to-side patrol movement."""
        self.x += self.current_speed * self.movement_direction
        if self.x + self.width > WIDTH - self.boundary_margin:
            self.x = WIDTH - self.width - self.boundary_margin
            self.movement_direction = -1
        elif self.x < self.boundary_margin:
            self.x = self.boundary_margin
            self.movement_direction = 1

    def update(self, boss_bullets_list, scatter_bullets_list, player_rect):
        """
        Updates the boss's state, movement, attacks, and timers.

        Args:
            boss_bullets_list: List to add boss's regular bullets to.
            scatter_bullets_list: List to add boss's scatter bullets to.
            player_rect: The player's pygame.Rect for aiming and collision.
        """
        if self.health <= 0: return

        self._update_enrage_status()
        self.state_timer += 1

        # Standard horizontal movement if not in a special action state
        if not self.is_dashing_phase_b and self.battle_state not in ["PHASE_B_WINDUP", "PHASE_B_DASHING", "PHASE_B_SCATTER"]:
            self._handle_standard_horizontal_movement()

        self.vertical_bob_timer += self.vertical_bob_speed
        offset_y = math.sin(self.vertical_bob_timer) * (HEIGHT * self.vertical_bob_amplitude_ratio)
        self.rect.x = int(self.x)
        self.rect.y = int(min(max(self.initial_y + offset_y, HEIGHT * 0.0166), HEIGHT - self.height - (HEIGHT*0.0166))) # 10, HEIGHT - self.h - 10

        if self.battle_state == "ENTERING":
            print("Boss entering, preparing for Phase A transition")
            self._transition_to_phase("A")

        elif self.battle_state == "PHASE_TRANSITION":
            self.transition_timer +=1
            # Particle generation scaled by FPS
            if self.transition_timer % max(1, int(5 * (60/FPS))) == 0 and len(self.transition_particles) < 20:
                p_color = ORANGE
                if self.target_phase == "A": p_color = RED
                elif self.target_phase == "B": p_color = ORANGE
                elif self.target_phase == "C": p_color = YELLOW
                self.transition_particles.append(Particle(self.rect.centerx + random.uniform(-self.width/2, self.width/2),
                                                          self.rect.centery + random.uniform(-self.height/2, self.height/2),
                                                          p_color, speed_ratio=random.uniform(0.000625,0.0025), # 0.5 to 2.0
                                                          size_ratio=random.uniform(0.0025,0.00625), # 2 to 5
                                                          lifetime_ratio=0.4)) # FPS*0.4
            for p in self.transition_particles[:]:
               p.update()
               if not p.is_alive(): self.transition_particles.remove(p)

            if self.transition_timer >= self.transition_duration_frames:
                self.main_cycle_state = self.target_phase
                self.transition_timer = 0
                self.transition_particles.clear()
                if self.target_phase == "A":
                    self.battle_state = "PHASE_A_SHOOT"; self.phase_a_salvos_done_this_round = 0
                elif self.target_phase == "B":
                    self.battle_state = "PHASE_B_WINDUP"; self.phase_b_dashes_performed_this_cycle = 0
                elif self.target_phase == "C":
                    self.battle_state = "PHASE_C_SHOOT"; self.phase_c_shots_fired_this_cycle = 0
                self.state_timer = 0

        elif self.battle_state in ["PHASE_A_SHOOT", "PHASE_A_DELAY"]:
            self._update_phase_a(boss_bullets_list, player_rect)

        elif self.battle_state == "PHASE_B_WINDUP":
            self.is_shaking_for_windup = True
            self.windup_shot_timer += 1
            windup_shoot_interval_frames = int(FPS * 0.5)
            if self.windup_shot_timer >= windup_shoot_interval_frames:
                self.windup_shot_timer = 0
                num_bullets_ring = 8
                angle_step_ring = (2 * math.pi) / num_bullets_ring
                for i in range(num_bullets_ring):
                    angle = i * angle_step_ring
                    self._fire_bullet(boss_bullets_list, angle, speed_mult=0.7, bullet_speed_override_ratio=0.003125) # 2.5

            if self.state_timer >= self.PHASE_B_WINDUP_DURATION_FRAMES:
                self.is_shaking_for_windup = False
                self.is_dashing_phase_b = True
                if player_rect:
                    self.phase_b_dash_target_x = player_rect.centerx
                    self.phase_b_dash_target_y = player_rect.centery + player_rect.height
                else:
                    self.phase_b_dash_target_x = WIDTH / 2
                    self.phase_b_dash_target_y = HEIGHT - (HEIGHT * 0.0833) # HEIGHT - 50
                self.battle_state = "PHASE_B_DASHING"
                self.windup_shot_timer = 0
                self.state_timer = 0

        elif self.battle_state == "PHASE_B_DASHING":
            dx = self.phase_b_dash_target_x - self.rect.centerx            dy = self.phase_b_dash_target_y - self.rect.centery
            dist = math.hypot(dx, dy)

            current_dash_s_abs = self.current_phase_b_dash_speed # Already scaled
            if self.is_enraged: current_dash_s_abs = (WIDTH * self.PHASE_B_DASH_SPEED_BASE_RATIO) * self.enraged_dash_speed_mult
            # else: current_dash_s_abs is already base scaled speed

            if dist > current_dash_s_abs:
                self.x += (dx / dist) * current_dash_s_abs
                self.y += (dy / dist) * current_dash_s_abs
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
            else:
                self.is_dashing_phase_b = False
                self.battle_state = "PHASE_B_SCATTER"
                self.state_timer = 0

            if self.rect.left < 0 or self.rect.right > WIDTH or self.rect.top < 0 or self.rect.bottom > HEIGHT * 0.95:
                self.is_dashing_phase_b = False
                self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
                self.x = self.rect.x; self.y = self.rect.y
                self.battle_state = "PHASE_B_SCATTER"
                self.state_timer = 0

        elif self.battle_state == "PHASE_B_SCATTER":
            scatter_angles = [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]
            scatter_bullet_color = YELLOW
            current_scatter_speed = WIDTH * self.PHASE_B_SCATTER_SPEED_RATIO
            for angle in scatter_angles:
                scatter_bullets_list.append(
                    ScatterBullet(self.rect.centerx, self.rect.centery, angle, current_scatter_speed, color=scatter_bullet_color))
            play_sound(enemy_shoot_sound if enemy_shoot_sound else None)

            self.phase_b_dashes_performed_this_cycle += 1
            self.state_timer = 0
            if self.phase_b_dashes_performed_this_cycle >= self.PHASE_B_DASHES_PER_CYCLE:
                self._transition_to_phase("C")
            else:
                self.battle_state = "PHASE_B_POST_DASH_COOLDOWN"

        elif self.battle_state == "PHASE_B_POST_DASH_COOLDOWN":
            if self.state_timer >= self.PHASE_B_POST_SCATTER_COOLDOWN_FRAMES:
                 self.battle_state = "PHASE_B_WINDUP"
                 self.state_timer = 0

        elif self.battle_state == "PHASE_C_SHOOT":
            actual_shoot_interval_c = self.PHASE_C_SHOOT_INTERVAL_FRAMES

            if self.state_timer >= actual_shoot_interval_c:
                player_angle = self._get_aim_angle_to_player(player_rect)

                current_homing_s_abs = self.current_phase_c_homing_strength # Already scaled by enrage if needed
                current_bullet_s_abs = self.current_phase_c_bullet_speed # Already scaled by enrage if needed

                self._fire_bullet(boss_bullets_list, player_angle,
                                  is_homing=True, homing_strength=current_homing_s_abs,
                                  bullet_speed_override_ratio=None) # Pass absolute speed directly
                self.phase_c_shots_fired_this_cycle += 1
                self.state_timer = 0

                if self.phase_c_shots_fired_this_cycle >= self.PHASE_C_TOTAL_SHOTS_PER_CYCLE:
                    self._transition_to_phase("A")

            self.phase_c_move_timer +=1
            if self.phase_c_move_timer >= self.PHASE_C_MOVE_INTERVAL_FRAMES:
                self.phase_c_move_dir *= -1
                self.phase_c_move_timer = 0
            self.x += self.phase_c_move_dir * (self.current_speed * 0.5) # Slower movement
            self.x = max(self.boundary_margin, min(self.x, WIDTH - self.width - self.boundary_margin))


        if self.is_flashing:
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.is_flashing = False

        for p in self.hit_spark_particles[:]:
            p.update()
            if not p.is_alive():
                self.hit_spark_particles.remove(p)
        for p in self.pixel_fragment_particles[:]:
            p.update()
            if not p.is_alive():

                self.pixel_fragment_particles.remove(p)

    def draw(self, surface):
        """Draws the boss and its effects onto the given surface."""
        if not self.image_base: # Should not happen if initialized correctly
            pygame.draw.rect(surface, (180,0,0), self.rect) # Fallback draw
            return

        current_base_image = self.image_base
        if self.battle_state == "PHASE_TRANSITION":
            current_base_image = self.image_base # Default during transition
        elif self.main_cycle_state == "A" and self.image_phase_a_tint:
            current_base_image = self.image_phase_a_tint
        elif self.main_cycle_state == "B" and self.image_phase_b_tint:
            current_base_image = self.image_phase_b_tint
        elif self.main_cycle_state == "C" and self.image_phase_c_tint:
            current_base_image = self.image_phase_c_tint
        # If a phase-specific tint image is missing, it will default to self.image_base

        # Start with a copy of the selected base image for modifications
        image_to_render_now = current_base_image.copy()
        draw_pos_x, draw_pos_y = self.rect.topleft

        if self.is_shaking_for_windup or self.battle_state == "PHASE_TRANSITION":
            shake_val_abs = int(WIDTH * 0.00375) # 3 for WIDTH 800
            draw_pos_x += random.randint(-shake_val_abs, shake_val_abs)
            draw_pos_y += random.randint(-shake_val_abs, shake_val_abs)

        if self.is_flashing:
            flash_color_to_use = self.flash_color
            if self.is_enraged:
                flash_color_to_use = RED
            flash_surface_render = pygame.Surface(image_to_render_now.get_size(), pygame.SRCALPHA)
            flash_surface_render.fill((flash_color_to_use[0], flash_color_to_use[1], flash_color_to_use[2], 128))
            image_to_render_now.blit(flash_surface_render, (0,0), special_flags=pygame.BLEND_RGB_ADD)

        surface.blit(image_to_render_now, (draw_pos_x, draw_pos_y))

        if self.battle_state == "PHASE_TRANSITION":
            for p in self.transition_particles: p.draw(surface)

        if self.is_enraged:
            enrage_overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            enrage_overlay.fill((DARK_RED[0], DARK_RED[1], DARK_RED[2], 40))
            surface.blit(enrage_overlay, (draw_pos_x, draw_pos_y), special_flags=pygame.BLEND_RGBA_ADD)

        for p in self.hit_spark_particles: p.draw(surface)
        for p in self.pixel_fragment_particles: p.draw(surface)

    def draw_health_bar(self, surface):
        if self.health > 0:
            bar_width_abs = WIDTH * 0.25 # 200 for WIDTH 800
            bar_height_abs = HEIGHT * 0.0333 # 20 for HEIGHT 600
            fill_width_abs = int((self.health / self.max_health) * bar_width_abs)
            bar_y_pos = int(HEIGHT * 0.0333) # 20 for HEIGHT 600
            outline_rect = pygame.Rect(WIDTH // 2 - bar_width_abs // 2, bar_y_pos, bar_width_abs, bar_height_abs)
            fill_rect = pygame.Rect(WIDTH // 2 - bar_width_abs // 2, bar_y_pos, fill_width_abs, bar_height_abs)
            pygame.draw.rect(surface, RED, fill_rect)
            pygame.draw.rect(surface, WHITE, outline_rect, int(bar_height_abs * 0.1)) # Border thickness relative to bar height

    def take_damage(self, amount=1, impact_point=None):
        """Applies damage to the boss, triggers visual feedback, and checks for defeat."""
        if self.health <= 0: return True
        self.health -= amount
        self.hit_flash()
        self._update_enrage_status()

        spark_spawn_x, spark_spawn_y = impact_point if impact_point else self.rect.center
        num_sparks = random.randint(15, 25)
        for _ in range(num_sparks):
            self.hit_spark_particles.append(SparkParticle(spark_spawn_x, spark_spawn_y))

        if self.is_enraged:
            num_fragments = random.randint(8, 15)
            for _ in range(num_fragments):
                edge = random.choice(['top', 'bottom', 'left', 'right'])
                px, py = self.rect.centerx, self.rect.centery
                initial_angle = 0
                if edge == 'top':
                    px = random.uniform(self.rect.left, self.rect.right); py = self.rect.top
                    initial_angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
                elif edge == 'bottom':
                    px = random.uniform(self.rect.left, self.rect.right); py = self.rect.bottom
                    initial_angle = random.uniform(math.pi * 0.15, math.pi * 0.85)
                elif edge == 'left':
                    px = self.rect.left; py = random.uniform(self.rect.top, self.rect.bottom)
                    initial_angle = random.uniform(math.pi * 0.65, math.pi * 1.35)
                elif edge == 'right':
                    px = self.rect.right; py = random.uniform(self.rect.top, self.rect.bottom)
                    initial_angle = random.uniform(-math.pi * 0.35, math.pi * 0.35)
                fragment_colors = [RED, ORANGE, YELLOW, WHITE, (180,180,180)]
                self.pixel_fragment_particles.append(PixelFragmentParticle(px, py, initial_angle, color=random.choice(fragment_colors)))

        if self.health <= 0:
            self.health = 0
            return True
        return False

    def hit_flash(self):
        self.is_flashing = True
        self.flash_timer = self.flash_duration_frames

    def reset_for_new_fight(self):
        """Resets the boss to its initial state for a new encounter."""
        self.health = self.max_health
        self.battle_state = "ENTERING"
        self.state_timer = 0
        self.is_enraged = False
        self.phase_a_salvos_done_this_round = 0
        self.phase_b_dashes_performed_this_cycle = 0
        self.phase_c_shots_fired_this_cycle = 0
        self.main_cycle_state = "A" # Start with Phase A behavior
        self.target_phase = "A" # Initial target phase
        self.x = WIDTH // 2 - self.width // 2
        self.y = self.initial_y
        self.current_phase_b_dash_speed = WIDTH * self.PHASE_B_DASH_SPEED_BASE_RATIO
        self.current_phase_c_bullet_speed = WIDTH * self.PHASE_C_BULLET_SPEED_BASE_RATIO
        self.current_phase_c_homing_strength = self.PHASE_C_HOMING_STRENGTH_BASE
        self.hit_spark_particles.clear()
        self.pixel_fragment_particles.clear()
    pass