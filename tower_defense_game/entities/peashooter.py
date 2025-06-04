import pygame
import os
# Standard library imports first

# Import local modules (ensure sys.path is set correctly by your entry point)
from entities.unit import Plant  # Base class for plants
from entities.projectile import Projectile, FrozenProjectile, FireProjectile # Import new projectile types

# Module global: Determine the project root directory (used for asset paths).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Peashooter(Plant):
    """
    A standard plant that shoots single peas at a regular interval.
    """
    IMAGE_FILENAME = None  # Visuals handled by AnimatedPeashooter
    FIRE_INTERVAL_MS = 1500  # Shoots every 1.5 seconds
    PROJECTILE_DAMAGE = 20
    PROJECTILE_SPEED = 5 # px/frame

    def __init__(self, game, grid_pos, cell_center_pos, projectile_image_surface, hp=100,
                 name="Peashooter", **other_kwargs): # Added projectile_image_surface
        """
        Initializes a Peashooter plant.

        Args:
            game: Reference to the main game controller object, used for adding projectiles
                  to a global list (e.g., game.projectiles).
            grid_pos (tuple): (col, row) position on the grid.
            cell_center_pos (tuple): (x, y) pixel center of the grid cell for positioning.
            hp (int): Health points for the plant.
            projectile_image_surface (pygame.Surface): The image for the projectile.
            name (str): Name of the plant.
            **other_kwargs: Additional keyword arguments for the base Plant class.
        """
        # image_path = os.path.join(PROJECT_ROOT, "assets", "images", Peashooter.IMAGE_FILENAME) if Peashooter.IMAGE_FILENAME else None
        # Base Plant class's fire_rate is in seconds
        super().__init__(grid_pos, cell_center_pos, hp=hp,
                         fire_rate=(Peashooter.FIRE_INTERVAL_MS / 1000.0),
                         damage=Peashooter.PROJECTILE_DAMAGE, # Stored as self.damage
                         name=name, image_path=None, **other_kwargs)
        self.game = game  # Store game reference
        self.projectile_image_surface = projectile_image_surface

    def update(self, enemies):
        """
        Updates the Peashooter. Handles its firing logic.
        Projectiles are added to the game's global projectile list.
        """
        if self.hp <= 0:
            self.kill()  # Remove from sprite groups if HP is depleted
            return
        
        # print(f"[DEBUG {self.name}] Update called. HP: {self.hp}, Last shot: {self.last_shot_time_ms}, Fire rate: {self.fire_rate_ms}") # Optional: General update call
        
        # Firing logic using self.last_shot_time_ms and self.fire_rate_ms from base Plant
        current_time_ms = pygame.time.get_ticks()
        if current_time_ms - self.last_shot_time_ms >= self.fire_rate_ms:
            print(f"[DEBUG {self.name}] Firing condition met. Time: {current_time_ms}")
            # Calculate projectile starting position (e.g., from the "mouth" of the plant)
            proj_start_x = self.rect.right - 10 # Adjusted for better visual placement
            proj_start_y = self.rect.centery

            new_projectile = Projectile(pos=(proj_start_x, proj_start_y),
                                        damage=self.damage, # Use self.damage from base
                                        speed=Peashooter.PROJECTILE_SPEED,
                                        image_surface=self.projectile_image_surface)

            # Add to the game's central projectile list
            if hasattr(self.game, 'projectiles') and isinstance(self.game.projectiles, list):
                print(f"[DEBUG {self.name}] Attempting to fire pea. Projectiles before: {len(self.game.projectiles)}")
                self.game.projectiles.append(new_projectile)
                print(f"[DEBUG {self.name}] Pea added. Projectiles after: {len(self.game.projectiles)}")
                # Tell visual component to play attack animation
                if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action'):
                    print(f"[DEBUG {self.name}] Telling visual_component ({type(self.visual_component)}) to Attack.")
                    self.visual_component.set_action("Attack") # THIS IS THE KEY LINE
                else:
                    if not hasattr(self, 'visual_component'):
                        print(f"[DEBUG {self.name}] Error: Plant has no visual_component attribute.")
                    elif not self.visual_component:
                        print(f"[DEBUG {self.name}] Error: Plant's visual_component is None.")
                    elif not hasattr(self.visual_component, 'set_action'):
                        print(f"[DEBUG {self.name}] Error: Plant's visual_component does not have set_action method.")

            self.last_shot_time_ms = current_time_ms # Reset cooldown timer


class SnowPea(Plant):
    """
    A plant that shoots frozen peas, which damage and slow enemies.
    """
    IMAGE_FILENAME = None # Visuals handled by AnimatedPeashooter
    FIRE_INTERVAL_MS = 1800  # Shoots every 1.8 seconds
    PROJECTILE_DAMAGE = 20
    PROJECTILE_SPEED = 5 # px/frame
    SLOW_EFFECT_DURATION_S = 2.0  # Duration of slow in seconds
    SLOW_EFFECT_FACTOR = 0.5    # Reduces enemy speed to 50%

    def __init__(self, game, grid_pos, cell_center_pos, projectile_image_surface, hp=100,
                 name="SnowPea", **other_kwargs): # Added projectile_image_surface
        """
        Initializes a SnowPea plant.
        Args:
            game: Reference to the main game controller.
            grid_pos (tuple): (col, row) on the grid.
            cell_center_pos (tuple): (x, y) pixel center for positioning.
            hp (int): Health points.
            projectile_image_surface (pygame.Surface): The image for the projectile.
            name (str): Name of the plant.
            **other_kwargs: Additional args for Plant base.
        """
        # image_path = os.path.join(PROJECT_ROOT, "assets", "images", SnowPea.IMAGE_FILENAME) if SnowPea.IMAGE_FILENAME else None
        super().__init__(grid_pos, cell_center_pos, hp=hp,
                         fire_rate=(SnowPea.FIRE_INTERVAL_MS / 1000.0),
                         damage=SnowPea.PROJECTILE_DAMAGE,
                         name=name, image_path=None, **other_kwargs)
        self.game = game
        self.projectile_image_surface = projectile_image_surface

    def update(self, enemies):
        """
        Updates the SnowPea, handling firing of frozen projectiles.
        """
        if self.hp <= 0:
            self.kill()
            return

        current_time_ms = pygame.time.get_ticks()
        if current_time_ms - self.last_shot_time_ms >= self.fire_rate_ms:
            proj_start_x = self.rect.right - 10
            proj_start_y = self.rect.centery

            new_projectile = FrozenProjectile(
                pos=(proj_start_x, proj_start_y),
                damage=self.damage,
                speed=SnowPea.PROJECTILE_SPEED,
                slow_duration=SnowPea.SLOW_EFFECT_DURATION_S,
                slow_factor=SnowPea.SLOW_EFFECT_FACTOR,
                image_surface=self.projectile_image_surface
            )

            if hasattr(self.game, 'projectiles') and isinstance(self.game.projectiles, list):
                self.game.projectiles.append(new_projectile)
                # Tell visual component to play attack animation
                if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action'):
                    self.visual_component.set_action("Attack")
            self.last_shot_time_ms = current_time_ms

    def draw(self, screen):
        """
        Draws the SnowPea plant.
        """
        if self.alive():
            screen.blit(self.image, self.rect)


class SnowPeaImproved(SnowPea): # Inherits from SnowPea
    """
    An improved SnowPea that fires more potent frozen peas.
    """
    # IMAGE_FILENAME can be the same as SnowPea or a new one if visuals differ
    # For this example, we assume the plant visual is the same as SnowPea,
    # but the projectile is different.
    FIRE_INTERVAL_MS = 1500 # Shoots every 1.5 seconds
    PROJECTILE_DAMAGE = 25 # Overridden
    # PROJECTILE_SPEED is inherited (5 px/frame)
    SLOW_EFFECT_DURATION_S = 5.0 # Overridden
    # SLOW_EFFECT_FACTOR is inherited (0.5)

    def __init__(self, game, grid_pos, cell_center_pos, projectile_image_surface, hp=100, # projectile_image_surface is for the "improved_pea"
                 name="SnowPeaImproved", **other_kwargs):
        # Call SnowPea's init, but we'll use our own damage.
        # We can pass SnowPea.IMAGE_FILENAME explicitly if needed, or rely on SnowPea's.
        super().__init__(game, grid_pos, cell_center_pos, projectile_image_surface, hp, name, **other_kwargs)
        self.damage = SnowPeaImproved.PROJECTILE_DAMAGE # Ensure damage is set to improved value for this instance
        self.fire_rate_ms = SnowPeaImproved.FIRE_INTERVAL_MS # Override fire_rate_ms from Plant/SnowPea
        # self.projectile_image_surface is already set by SnowPea's __init__

    def update(self, enemies):
        """
        Updates the SnowPeaImproved, handling firing of improved frozen projectiles.
        """
        if self.hp <= 0:
            self.kill()
            return

        current_time_ms = pygame.time.get_ticks()
        if current_time_ms - self.last_shot_time_ms >= self.fire_rate_ms: # fire_rate_ms from SnowPea
            proj_start_x = self.rect.right - 10
            proj_start_y = self.rect.centery

            new_projectile = FrozenProjectile(
                pos=(proj_start_x, proj_start_y),
                damage=self.damage, # Uses SnowPeaImproved's damage
                speed=SnowPea.PROJECTILE_SPEED, # Inherited speed
                slow_duration=SnowPeaImproved.SLOW_EFFECT_DURATION_S, # Improved duration
                slow_factor=SnowPea.SLOW_EFFECT_FACTOR, # Inherited factor
                image_surface=self.projectile_image_surface # This should be the "improved_pea" image
            )

            if hasattr(self.game, 'projectiles') and isinstance(self.game.projectiles, list):
                self.game.projectiles.append(new_projectile)
                # Tell visual component to play attack animation
                if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action'):
                    self.visual_component.set_action("Attack") # SnowPeaImproved also uses "Attack" action name
            self.last_shot_time_ms = current_time_ms


class Repeater(Plant):
    """
    A plant that quickly shoots two peas in a single burst.
    """
    IMAGE_FILENAME = None # Visuals handled by AnimatedPeashooter
    BURST_FIRE_INTERVAL_MS = 1800  # Time between the start of each burst
    PROJECTILE_DAMAGE = 20
    PROJECTILE_SPEED = 5 # px/frame
    DELAY_BETWEEN_SHOTS_MS = 200  # Delay between the two shots in a burst

    def __init__(self, game, grid_pos, cell_center_pos, projectile_image_surface, hp=100,
                 name="Repeater", **other_kwargs): # Added projectile_image_surface
        """
        Initializes a Repeater plant.
        Args:
            game: Reference to the main game controller.
            grid_pos (tuple): (col, row) on the grid.
            cell_center_pos (tuple): (x, y) pixel center for positioning.
            hp (int): Health points.
            projectile_image_surface (pygame.Surface): The image for the projectile.
            name (str): Name of the plant.
            **other_kwargs: Additional args for Plant base.
        """
        # image_path = os.path.join(PROJECT_ROOT, "assets", "images", Repeater.IMAGE_FILENAME) if Repeater.IMAGE_FILENAME else None
        # The base fire_rate_ms will time the start of each burst
        super().__init__(grid_pos, cell_center_pos, hp=hp,
                         fire_rate=(Repeater.BURST_FIRE_INTERVAL_MS / 1000.0),
                         damage=Repeater.PROJECTILE_DAMAGE,
                         name=name, image_path=None, **other_kwargs)
        self.game = game
        self.projectile_image_surface = projectile_image_surface
        self._is_firing_second_shot = False
        self._time_first_shot_fired = 0

    def _fire_one_pea(self):
        """Helper method to create and fire a single pea projectile."""
        proj_start_x = self.rect.right - 10
        proj_start_y = self.rect.centery
        new_projectile = Projectile(pos=(proj_start_x, proj_start_y),
                                    damage=self.damage,
                                    speed=Repeater.PROJECTILE_SPEED,
                                    image_surface=self.projectile_image_surface)
        if hasattr(self.game, 'projectiles') and isinstance(self.game.projectiles, list):
            self.game.projectiles.append(new_projectile)
            # Tell visual component to play attack animation (only for the first shot of the burst)
            if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action') and not self._is_firing_second_shot:
                 self.visual_component.set_action("Attack")

    def update(self, enemies):
        """
        Updates the Repeater, handling its burst fire logic.
        """
        if self.hp <= 0:
            self.kill()
            return

        current_time_ms = pygame.time.get_ticks()

        if self._is_firing_second_shot:
            # Check if it's time for the second shot of the burst
            if current_time_ms - self._time_first_shot_fired >= Repeater.DELAY_BETWEEN_SHOTS_MS:
                self._fire_one_pea()
                self._is_firing_second_shot = False
                # The main cooldown (self.last_shot_time_ms) was set when the first shot fired,
                # so the next burst is timed correctly from the start of the previous burst.
        else:
            # Check if it's time to start a new burst (fire the first shot)
            if current_time_ms - self.last_shot_time_ms >= self.fire_rate_ms:
                self._fire_one_pea()  # Fire the first shot
                # Attack animation is triggered within _fire_one_pea helper if conditions are met
                if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action'):
                    self.visual_component.set_action("Attack")
                self.last_shot_time_ms = current_time_ms  # Reset burst cooldown timer
                self._time_first_shot_fired = current_time_ms # Record time for second shot
                self._is_firing_second_shot = True # Set state to fire second shot

    def draw(self, screen):
        """
        Draws the Repeater plant.
        """
        if self.alive():
            screen.blit(self.image, self.rect)


class GatlingPea(Plant):
    """
    A plant that rapidly shoots four fire peas in a burst.
    """
    IMAGE_FILENAME = None # Visuals handled by AnimatedPeashooter
    BURST_FIRE_INTERVAL_MS = 1800
    PROJECTILE_DAMAGE = 20
    PROJECTILE_SPEED = 5 # px/frame
    SHOTS_IN_BURST = 4
    DELAY_BETWEEN_SHOTS_MS = 150

    def __init__(self, game, grid_pos, cell_center_pos, projectile_image_surface, hp=125, # projectile_image_surface for fire_pea
                 name="GatlingPea", **other_kwargs):
        # image_path = os.path.join(PROJECT_ROOT, "assets", "images", GatlingPea.IMAGE_FILENAME) if GatlingPea.IMAGE_FILENAME else None
        super().__init__(grid_pos, cell_center_pos, hp=hp,
                         fire_rate=(GatlingPea.BURST_FIRE_INTERVAL_MS / 1000.0),
                         damage=GatlingPea.PROJECTILE_DAMAGE,
                         name=name, image_path=None, **other_kwargs)
        self.game = game
        self.projectile_image_surface = projectile_image_surface # This should be the "fire_pea" image
        self._shots_fired_in_current_burst = 0
        self._time_last_shot_in_burst_fired = 0

    def _fire_one_fire_pea(self):
        """Helper method to create and fire a single fire pea projectile."""
        proj_start_x = self.rect.right - 10
        proj_start_y = self.rect.centery
        new_projectile = FireProjectile(pos=(proj_start_x, proj_start_y),
                                        damage=self.damage,
                                        speed=GatlingPea.PROJECTILE_SPEED,
                                        image_surface=self.projectile_image_surface)
        if hasattr(self.game, 'projectiles') and isinstance(self.game.projectiles, list):
            self.game.projectiles.append(new_projectile)
            # Trigger attack animation (only for the first shot of the burst)
            if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action') and self._shots_fired_in_current_burst <= 1 : # First shot of burst
                self.visual_component.set_action("Attack")

    def update(self, enemies):
        if self.hp <= 0:
            self.kill()
            return

        current_time_ms = pygame.time.get_ticks()

        # Managing shots within a burst
        if self._shots_fired_in_current_burst > 0 and self._shots_fired_in_current_burst < GatlingPea.SHOTS_IN_BURST:
            if current_time_ms - self._time_last_shot_in_burst_fired >= GatlingPea.DELAY_BETWEEN_SHOTS_MS:
                self._fire_one_fire_pea()
                self._shots_fired_in_current_burst += 1
                self._time_last_shot_in_burst_fired = current_time_ms
                if self._shots_fired_in_current_burst >= GatlingPea.SHOTS_IN_BURST:
                    self._shots_fired_in_current_burst = 0 # Reset for next burst
        # Starting a new burst
        elif self._shots_fired_in_current_burst == 0: # Ready to start a new burst
            if current_time_ms - self.last_shot_time_ms >= self.fire_rate_ms: # fire_rate_ms is the burst interval
                self._fire_one_fire_pea()
                # Attack animation triggered within _fire_one_fire_pea helper if conditions met
                if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_action'):
                    self.visual_component.set_action("Attack")
                self.last_shot_time_ms = current_time_ms # Reset cooldown for the START of the burst
                self._time_last_shot_in_burst_fired = current_time_ms
                self._shots_fired_in_current_burst = 1

    def draw(self, screen):
        if self.alive():
            screen.blit(self.image, self.rect)
