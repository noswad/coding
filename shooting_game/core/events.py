import pygame
import random # Moved import to top level
from objects.enemy import Enemy # Added import for Enemy class
from core.game_state import GameState # Import GameState enum
from settings import ENEMY_SIZE_RATIO, BOSS_APPEAR_ROUND, WIDTH, HEIGHT # Added necessary imports from settings


def handle_events(game_state, player, enemies, bullets, enemy_bullets, boss_bullets, scatter_bullets, escorts, sounds_loaded, music_loaded, sounds_dir, start_sound, reset_game_state, round_number, BOSS_APPEAR_ROUND, WIDTH, HEIGHT, ENEMY_SIZE_RATIO):
    """
    處理所有 pygame 事件，並根據遊戲狀態與輸入進行狀態切換或遊戲控制。
    回傳 (running, game_state, 其他必要變數...)
    """
    running = True
    active_boss = None
    boss_spawned_this_round = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == GameState.START:
                    game_state = GameState.PLAYING
                    reset_game_state()
            elif event.key == pygame.K_r and game_state == GameState.GAME_OVER:
                game_state = GameState.PLAYING
                reset_game_state()
            elif event.key == pygame.K_b:
                if game_state in [GameState.START, GameState.PLAYING, GameState.GAME_OVER]:
                    print("DEBUG: Jumping to Boss Round!")
                    game_state = GameState.PLAYING
                    round_number = BOSS_APPEAR_ROUND
                    boss_spawned_this_round = False
                    active_boss = None
                    player.lives = 3
                    player.x = WIDTH // 2 - player.width // 2
                    player.y = HEIGHT - player.height - (HEIGHT*0.0166)
                    player.invincible = False
                    enemies.clear()
                    bullets.clear()
                    enemy_bullets.clear()
                    boss_bullets.clear()
                    scatter_bullets.clear()
                    escorts.clear()
                    # 生成一些敵人
                    for _ in range(random.randint(1,3)):
                        enemy_x_ratio = random.uniform(ENEMY_SIZE_RATIO[0], 1.0 - ENEMY_SIZE_RATIO[0] * 2)
                        enemy_y_ratio = random.uniform(ENEMY_SIZE_RATIO[1], 0.25)
                        enemies.append(Enemy(enemy_x_ratio, enemy_y_ratio))
                    if sounds_loaded and music_loaded:
                        pygame.mixer.music.stop()
        elif event.type == pygame.MOUSEMOTION:
            if game_state in [GameState.PLAYING, GameState.BOSS_FIGHT]:
                player.x = event.pos[0] - player.width // 2
                player.rect.x = player.x

    return running, game_state, active_boss, boss_spawned_this_round, round_number