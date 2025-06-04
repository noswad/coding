import sys
import pygame
import os
import resources
from settings import *
from core.game_state import GameState, game_state
from core.utils import load_high_score, save_high_score
from objects.player import Player
from objects.enemy import Enemy, EliteEnemy
from objects.boss import BossLv1
from objects.bullet import Bullet, EnemyBullet, BossBullet, ScatterBullet
from objects.particle import Particle, Explosion, BloodParticle, SparkParticle, PixelFragmentParticle
from objects.star import Star
from core.events import handle_events
from ui.hud import draw_score, draw_lives, draw_round
from ui.screens import draw_start_screen, draw_game_over_screen

# --- 初始化 ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# 載入資源
fonts = resources.init_resources()
chinese_font = fonts['chinese_font']
title_font = fonts['title_font']
small_font = fonts['small_font']

# 檢查圖片與音效是否正確載入
def check_resource_loaded(resource, name):
    if resource is None:
        print(f"[警告] {name} 載入失敗，請檢查資源檔案與路徑。")

check_resource_loaded(resources.background_img, "背景圖片 background_img")
check_resource_loaded(resources.player_img, "主角圖片 player_img")
check_resource_loaded(resources.enemy_img, "敵人圖片 enemy_img")
check_resource_loaded(resources.shoot_sound, "射擊音效 shoot_sound")
check_resource_loaded(resources.explosion_sound, "爆炸音效 explosion_sound")
check_resource_loaded(resources.gamestart_music_path, "開始音樂 gamestart.mp3")

# Determine resource loading status (used by reset_game_state and passed to handle_events)
sounds_loaded_main = bool(resources.shoot_sound and resources.explosion_sound)
music_file_path_main = os.path.join(BASE_DIR, SOUND_DIR, "background.mp3")
music_loaded_main = os.path.exists(music_file_path_main)
gamestart_music_loaded = resources.gamestart_music_path is not None

# 初始化遊戲物件
def reset_game_state():
    global player, enemies, bullets, enemy_bullets, boss_bullets, scatter_bullets, escorts, explosions
    global round_number, boss_spawned_this_round, active_boss, score, dive_timer, player_shoot_timer, current_blood_spray
    player = Player(0.5, 1.0 - (70/HEIGHT))
    enemies = init_enemies()
    bullets, enemy_bullets, boss_bullets, scatter_bullets, escorts, explosions = [], [], [], [], [], []
    round_number = 1
    boss_spawned_this_round = False
    active_boss = None
    score = 0
    dive_timer = 0
    player_shoot_timer = 0
    current_blood_spray = None
    # 只播放 gamestart.mp3，背景音樂延後到 PLAYING 狀態
    if gamestart_music_loaded:
        resources.play_gamestart_music()
    else:
        print("[警告] 無法播放開始音樂，gamestart.mp3 未載入。")

def play_background_music():
    if music_loaded_main:
        try:
            pygame.mixer.music.load(music_file_path_main)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[警告] 背景音樂載入或播放失敗: {e}")
    else:
        print("[警告] 找不到背景音樂檔案，請檢查 sounds/background.mp3 是否存在。")

def init_enemies():
    enemies = []
    # Basic enemy generation for testing
    # Replace with your actual enemy generation logic
    num_enemies_to_spawn = min(5 + round_number, 10) # Example: more enemies in later rounds
    for i in range(num_enemies_to_spawn):
        x_ratio = (i % NUM_COLS) * (1.0 / (NUM_COLS + 1)) + ENEMY_COL_SPACING_RATIO
        y_ratio = ENEMY_START_Y_RATIO + (i // NUM_COLS) * ENEMY_ROW_SPACING_RATIO
        if random.random() < 0.2: # 20% chance for an elite enemy
            enemies.append(EliteEnemy(x_ratio, y_ratio))
        else:
            enemies.append(Enemy(x_ratio, y_ratio))
    return enemies

def create_explosion(x, y, size_multiplier=1.0):
    explosions.append(Explosion(x, y, size_multiplier=size_multiplier))

# 讀取最高分
high_score = load_high_score()

# 星星背景
stars = [Star() for _ in range(STAR_COUNT)]

# --- 遊戲主迴圈 ---
running = True
reset_game_state()
background_music_played = False

while running:
    dt_ms = clock.tick(FPS)

    # Event handling using handle_events
    current_running_status, new_game_state, new_active_boss, new_boss_spawned, updated_round_number = \
        handle_events(game_state, player, enemies, bullets, enemy_bullets, boss_bullets, scatter_bullets, escorts,
                      sounds_loaded_main, music_loaded_main,
                      SOUND_DIR, resources.gamestart_music_path, reset_game_state, round_number,
                      BOSS_APPEAR_ROUND, WIDTH, HEIGHT, ENEMY_SIZE_RATIO)

    running = current_running_status
    if game_state != new_game_state: # If state changed, potentially reset background music flag
        background_music_played = False
    game_state = new_game_state # Apply new game state
    if new_active_boss is not None:
        active_boss = new_active_boss
    boss_spawned_this_round = new_boss_spawned
    round_number = updated_round_number # Update round_number from handle_events

    keys = pygame.key.get_pressed()

    # 狀態判斷與遊戲邏輯
    if game_state == GameState.START:
        background_music_played = False  # 確保每次回到 START 都會重播背景音樂
    elif game_state == GameState.PLAYING:
        if not background_music_played:
            play_background_music()
            background_music_played = True

        # --- Player Updates ---
        # Example: Player Movement (replace with your preferred controls)
        player_speed = WIDTH * 0.007 # Example speed
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            player.update_position(x=player.x - player_speed * (dt_ms / (1000/FPS)))
        if keys[pygame.K_RIGHT] and player.rect.right < WIDTH:
            player.update_position(x=player.x + player_speed * (dt_ms / (1000/FPS)))
        
        # Example: Player Shooting
        player_shoot_timer += dt_ms
        if keys[pygame.K_SPACE] and player_shoot_timer >= PLAYER_SHOOT_INTERVAL_FRAMES * (1000/FPS): # K_SPACE for shooting
            bullets.append(Bullet(player.rect.centerx - (PLAYER_BULLET_SIZE_RATIO[0]*WIDTH)/2, player.rect.top))
            if sounds_loaded_main and resources.shoot_sound:
                resources.play_sound(resources.shoot_sound)
            player_shoot_timer = 0

        # --- Enemy Updates ---
        for enemy in enemies[:]:
            enemy.move() # Basic movement
            enemy.update() # For flashing or other timed effects
            # Add enemy shooting logic here if applicable
            # Add collision checks: player bullets vs enemies, player vs enemies

        # --- Bullet Updates ---
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        for e_bullet in enemy_bullets[:]:
            e_bullet.move()
            if e_bullet.rect.top > HEIGHT:
                enemy_bullets.remove(e_bullet)
            # Add collision checks: enemy bullets vs player

        # --- Explosion Updates ---
        for explosion in explosions[:]:
            explosion.update()
            if explosion.is_finished():
                explosions.remove(explosion)

        # Add other game logic:
        # - Spawning new enemies if current wave cleared
        # - Advancing rounds
        # - Checking for player death
        # - Transitioning to BOSS_INTRO_SEQUENCE or BOSS_FIGHT

    elif game_state == GameState.BOSS_INTRO_SEQUENCE:
        pass
    elif game_state == GameState.PLAYER_DYING:
        pass
    elif game_state == GameState.BOSS_FIGHT:
        # Add similar update logic for player, boss, boss bullets, escorts, collisions
        if active_boss: active_boss.update(boss_bullets, scatter_bullets, player.rect)
    elif game_state == GameState.GAME_OVER:
        save_high_score(high_score)

    # --- 畫面繪製 ---
    screen.fill(BLACK)
    if resources.background_img:
        screen.blit(resources.background_img, (0, 0))
    else:
        # 若背景圖未載入，填充灰色以利 debug
        screen.fill((30, 30, 30))
    for star in stars:
        star.update_position()
        star.draw(screen)

    if game_state == GameState.START:
        draw_start_screen(screen, title_font, chinese_font, small_font, high_score)
    elif game_state == GameState.PLAYING:
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for e_bullet in enemy_bullets:
            e_bullet.draw(screen)
        for explosion in explosions:
            explosion.draw(screen)
        draw_score(screen, small_font, score)
        draw_lives(screen, small_font, player.lives)
        draw_round(screen, small_font, round_number)
    elif game_state == GameState.BOSS_INTRO_SEQUENCE:
        pass
    elif game_state == GameState.PLAYER_DYING:
        player.draw(screen)
        if current_blood_spray:
            current_blood_spray.draw(screen)
    elif game_state == GameState.BOSS_FIGHT:
        if active_boss:
            active_boss.draw_health_bar(screen)
        for escort in escorts:
            escort.draw(screen)
        player.draw(screen)
        if active_boss:
            active_boss.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for b_bullet in boss_bullets:
            b_bullet.draw(screen)
        for s_bullet in scatter_bullets:
            s_bullet.draw(screen)
        for explosion in explosions:
            explosion.draw(screen)
        draw_score(screen, small_font, score)
        draw_lives(screen, small_font, player.lives)
    elif game_state == GameState.GAME_OVER:
        draw_game_over_screen(screen, title_font, chinese_font, score, high_score)

    pygame.display.flip()

pygame.quit()
sys.exit()