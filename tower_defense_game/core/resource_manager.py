import pygame

class ResourceManager:
    """
    Manages game resources like suns that appear on screen and can be collected.
    """
    def __init__(self, game_ref):
        """
        Initializes the ResourceManager.
        Args:
            game_ref: A reference to the main Game object.
        """
        self.game = game_ref
        self.suns = pygame.sprite.Group() # Use a sprite group for suns

    def add_sun(self, sun_instance):
        """Adds a Sun instance to be managed."""
        self.suns.add(sun_instance)
        # print(f"Sun added at {sun_instance.rect.center}. Total suns: {len(self.suns)}") # For debugging

    def update(self):
        """Updates all managed suns."""
        self.suns.update()
        # Suns should kill themselves if they time out or are collected.
        # The sprite group will automatically remove them.

    def draw(self, screen):
        """Draws all managed suns onto the screen."""
        self.suns.draw(screen)

    def handle_click(self, mouse_pos):
        """Checks if any sun was clicked, collects it, and returns its value."""
        for sun in self.suns:
            if sun.rect.collidepoint(mouse_pos) and not sun.is_dead: # Check is_dead for safety
                collected_value = sun.collect()
                if collected_value > 0:
                    sun.kill() # Remove from all sprite groups
                    return collected_value
        return 0