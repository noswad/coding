import pygame
import os
# Standard library imports first

# Local application imports. These rely on sys.path being correctly set
# by an entry point like core/game.py.
from entities.unit import Plant  # Base class for plants
from entities.resource import Sun

# Module global: Determine the project root directory (used for asset paths).
# __file__ is d:/coding/tower_defense_game/entities/sunflower.py
# os.path.dirname(__file__) is d:/coding/tower_defense_game/entities
# os.path.dirname(os.path.dirname(__file__)) is d:/coding/tower_defense_game
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Sunflower(Plant):
    """
    A plant that generates Sun resources at regular intervals.
    The generated Sun instances are passed to the game's resource manager
    for further handling, including animation and collection.
    """
    IMAGE_FILENAME = None    # Visuals handled by AnimatedSunflower
    GENERATION_INTERVAL_MS = 7000     # Generates Sun every 7 seconds
    DEFAULT_HP = 75                   # Default health points for a Sunflower

    def __init__(self, game, grid_pos, cell_center_pos, hp=DEFAULT_HP,
                 name="Sunflower", **other_kwargs):
        """
        Initializes a Sunflower plant.

        Args:
            game: Reference to the main game controller object.
                  It's expected to have a `resource_manager` attribute,
                  which in turn should have an `add_sun(sun_instance)` method.
            grid_pos (tuple): (col, row) position on the game grid.
            cell_center_pos (tuple): (x, y) pixel center of the grid cell.
                                     This is used for positioning the plant and as
                                     the target destination for the falling Sun.
            hp (int): Health points for the plant.
            name (str): Name of the plant type.
            **other_kwargs: Additional keyword arguments for the base Plant class.
        """
        # image_path = os.path.join(PROJECT_ROOT, "assets", "images", Sunflower.IMAGE_FILENAME) if Sunflower.IMAGE_FILENAME else None

        # The Plant base class uses 'fire_rate' in seconds for its action cooldown.
        # We'll use this mechanism for timing Sun generation.
        super().__init__(grid_pos, cell_center_pos, hp=hp,
                         fire_rate=(Sunflower.GENERATION_INTERVAL_MS / 1000.0),
                         name=name, image_path=None,
                         # Sunflowers don't have a direct 'damage' output like peashooters
                         damage=0,  # Explicitly set damage to 0 or omit if Plant handles it
                         **other_kwargs)
        self.game = game
        # The Plant base class initializes `self.last_shot_time_ms` which we use
        # for timing the sun generation. It's typically set to the creation time.

    def update(self, enemies=None): # Modified to accept enemies argument (but ignores it)
        """
        Updates the Sunflower's state. Handles Sun generation logic.
        This method is called typically once per game frame.
        The 'enemies' parameter is accepted for compatibility with the game loop.
        """
        if self.hp <= 0:
            self.kill()  # Mark for removal if HP is depleted
            return

        current_time_ms = pygame.time.get_ticks()

        # Check if it's time to generate a new Sun
        # self.fire_rate_ms and self.last_shot_time_ms are from the Plant base class
        if current_time_ms - self.last_shot_time_ms >= self.fire_rate_ms:
            # Define where the Sun appears (top-center of the Sunflower)
            spawn_pos_x = self.rect.centerx
            spawn_pos_y = self.rect.top

            # Define where the Sun should fall to (center of the Sunflower's cell)
            # self.rect.center was set by Plant using cell_center_pos
            target_pos = self.rect.center

            # Create a new Sun instance, using the AnimatedSunflower's sun_icon_image if available.
            sun_icon_image = None
            if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'sun_icon_image'):
                sun_icon_image = self.visual_component.sun_icon_image
            new_sun = Sun(initial_pos=(spawn_pos_x, spawn_pos_y), target_pos=target_pos, image=sun_icon_image)

            # Pass the new Sun to the game's resource manager
            if hasattr(self.game, 'resource_manager') and \
               hasattr(self.game.resource_manager, 'add_sun'):
                # Trigger glow animation on the visual component
                if hasattr(self, 'visual_component') and self.visual_component and hasattr(self.visual_component, 'set_state'):
                    print(f"[DEBUG {self.name} ID: {id(self)}] Telling visual_component to glow.") # DEBUG
                    self.visual_component.set_state("glow")
                self.game.resource_manager.add_sun(new_sun)
            else:
                # Log a warning if the resource manager or its method is not found
                print(f"Warning: {self.name} at {self.grid_pos} could not add Sun. "
                      "Ensure game.resource_manager.add_sun(sun_instance) exists.")

            self.last_shot_time_ms = current_time_ms  # Reset the generation timer

    def draw(self, screen):
        """
        Draws the Sunflower plant on the given screen.
        The Sun instances are expected to be drawn by the resource manager or a
        centralized game view, not directly by the Sunflower.
        """
        if self.alive():  # Only draw if the plant is active (not killed)
            screen.blit(self.image, self.rect)