import pygame
import random # Moved import to the top
from entities.enemy import Enemy

class WaveManager:
    """
    Manages the spawning of enemy waves based on predefined wave data.
    Handles delays between waves and intervals between enemy spawns within a wave.
    """
    def __init__(self, wave_data, spawn_callback):
        """
        wave_data: List of dicts, each dict describes a wave:
            {
                "count": int,  # number of enemies in this wave
                "enemy_type": class,  # enemy class (e.g., Enemy)
                "interval": float,  # seconds between spawns
                "start_delay": float,  # seconds delay before this wave starts
                "params": dict,  # extra params for enemy
            }
        spawn_callback: function to call with (enemy_instance) when spawning
        """
        self.wave_data = wave_data
        self.spawn_callback = spawn_callback
        self.current_wave_index = 0
        self.enemies_spawned = 0
        self.last_spawn_timestamp = 0  # Using 0 as a flag for first spawn in a wave
        self.wave_delay_start_timestamp = pygame.time.get_ticks() # Time when current delay period started
        self.in_wave = False
        self.finished = False

    def start_next_wave(self):
        if self.current_wave_index >= len(self.wave_data):
            self.finished = True
            return
        self.in_wave = True
        self.enemies_spawned = 0
        # self.wave_delay_start_timestamp is set when a wave *ends* or in __init__.
        # It's for the *delay* before this wave, not needed to be reset here.
        self.last_spawn_timestamp = 0 # Ensures first enemy spawns immediately if interval allows

    def update(self):
        if self.finished:
            return

        if not self.in_wave:
            # 準備下一波
            if self.current_wave_index >= len(self.wave_data): # All waves processed
                self.finished = True
                return
            
            wave_config = self.wave_data[self.current_wave_index]
            # Convert delay from seconds (in config) to milliseconds for get_ticks()
            start_delay_ms = wave_config.get("start_delay", 0) * 1000
            if pygame.time.get_ticks() - self.wave_delay_start_timestamp >= start_delay_ms:
                self.start_next_wave()
            return

        wave_config = self.wave_data[self.current_wave_index]
        count = wave_config["count"]
        # Convert interval from seconds (in config) to milliseconds
        interval_ms = wave_config["interval"] * 1000
        enemy_type = wave_config["enemy_type"]
        all_wave_params = wave_config.get("params", {})

        # 逐一生成敵人
        current_ticks = pygame.time.get_ticks()
        if self.enemies_spawned < count:
            if (current_ticks - self.last_spawn_timestamp >= interval_ms) or \
               (self.last_spawn_timestamp == 0 and self.enemies_spawned == 0): # Ensure first spawn
                   
                # 隨機選一行生成
                # Determine spawn row using specific params from all_wave_params
                spawn_row_override = all_wave_params.get("row", None)
                if spawn_row_override is None:
                    # Use max_row for random row selection, default to 4 if not specified
                    max_row_for_random_spawn = all_wave_params.get("max_row", 4) 
                    spawn_row_override = random.randint(0, max_row_for_random_spawn)
                y = 60 + spawn_row_override * 100  # 根據格子高度調整

                # Prepare kwargs for the enemy constructor, filtering out wave-manager specific params
                enemy_constructor_kwargs = {}
                # These are the keyword parameters Enemy.__init__ accepts
                accepted_by_enemy_init = ["hp", "speed", "attack_power", "attack_interval"]
                for key, value in all_wave_params.items():
                    if key in accepted_by_enemy_init:
                        enemy_constructor_kwargs[key] = value
                
                enemy = enemy_type(pos=(800, y), **enemy_constructor_kwargs)
                self.spawn_callback(enemy)
                self.enemies_spawned += 1
                self.last_spawn_timestamp = current_ticks
        else:
            # 等待所有敵人生成完畢後，進入下一波
            self.in_wave = False
            self.current_wave_index += 1
            self.wave_delay_start_timestamp = pygame.time.get_ticks() # Start timer for next wave's delay
            if self.current_wave_index >= len(self.wave_data):
                self.finished = True # All waves done

    def is_finished(self):
        return self.finished

# --- 範例波次設定 ---
def example_wave_data():
    # Enemy class is imported at the module level
    waves = []
    for i in range(5):
        waves.append({
            "count": 3 + i,  # 每波多一隻
            "enemy_type": Enemy,
            "interval": 1.5,  # Seconds, will be converted to ms by WaveManager
            "start_delay": 3.0 if i == 0 else 5.0, # Seconds
            "params": {"hp": 50 + i*10, "speed": 1 + i*0.2, "max_row": 4}
        })
    return waves

# --- Game 類別整合範例 ---
if __name__ == "__main__":
    # 假設有一個 enemies pygame.sprite.Group()
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    enemies = pygame.sprite.Group()

    def spawn_enemy(enemy):
        enemies.add(enemy)

    wave_manager = WaveManager(example_wave_data(), spawn_enemy)
    
    running = True
    # game_start_time = pygame.time.get_ticks() # Example: if you need an overall game timer

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(30) / 1000.0  # Delta time in seconds

        wave_manager.update()
        enemies.update(dt) # Pass delta time or other relevant params to enemy updates
        
        screen.fill((0, 0, 0))
        for e in enemies:
            e.draw(screen)
        pygame.display.flip()
        
        if wave_manager.is_finished() and not enemies:
            print("All waves finished!")
            running = False

    pygame.quit()