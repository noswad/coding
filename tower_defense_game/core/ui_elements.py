import pygame

class PlantCard:
    """
    Represents a plant card in the UI, holding its properties and state.
    """
    def __init__(self, plant_name, cost, cooldown_ms, icon_surface, plant_class_to_spawn,
                 cursor_image, asset_loader_type, visual_type_for_assets):
        """
        Args:
            plant_name (str): The display name of the plant.
            cost (int): The sun cost to plant this plant.
            cooldown_ms (int): The cooldown duration in milliseconds after planting.
            icon_surface (pygame.Surface): The image for the card (seed packet).
            plant_class_to_spawn (class): The actual plant logic class to instantiate.
            cursor_image (pygame.Surface): The image to use for the cursor when this card is selected.
            asset_loader_type (str): Type of asset loader ('sunflower' or 'peashooter').
            visual_type_for_assets (str): The specific visual type (e.g., 'Peashooter', 'SnowPea').
        """
        self.plant_name = plant_name
        self.cost = cost
        self.cooldown_ms = cooldown_ms
        self.icon_surface = icon_surface
        self.plant_class_to_spawn = plant_class_to_spawn
        self.cursor_image = cursor_image

        self.asset_loader_type = asset_loader_type
        self.visual_type_for_assets = visual_type_for_assets
        self.last_used_time = -float('inf') # Available immediately at game start
        self.is_selected = False # True if the player has picked this card

    def can_be_selected(self, current_sun_amount):
        """Checks if the card can be afforded and is not on cooldown."""
        return current_sun_amount >= self.cost and not self.is_on_cooldown()

    def start_cooldown(self):
        """Call this when the plant is successfully placed to start its cooldown."""
        self.last_used_time = pygame.time.get_ticks()
        self.is_selected = False # Planting usually deselects the card

    def is_on_cooldown(self):
        """Returns True if the card is currently on cooldown."""
        if self.cooldown_ms <= 0:
            return False
        return pygame.time.get_ticks() - self.last_used_time < self.cooldown_ms

    def get_cooldown_progress(self):
        """Returns cooldown progress: 1.0 (just used, full cooldown) to 0.0 (ready)."""
        if self.cooldown_ms <= 0 or not self.is_on_cooldown():
            return 0.0
        elapsed_time = pygame.time.get_ticks() - self.last_used_time
        return max(0.0, min(1.0, 1.0 - (elapsed_time / self.cooldown_ms)))