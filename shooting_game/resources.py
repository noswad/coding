import os
import pygame
from settings import BASE_DIR, IMAGE_DIR, SOUND_DIR

# 全域圖片資源
background_img = None
player_img = None
enemy_img = None
elite_enemy_img = None
boss_lv1_img = None
boss_lv1_orange_img = None
boss_lv1_red_img = None
boss_lv1_yellow_img = None
player_bullet_img = None
enemy_bullet_img = None
boss_bullet_img = None

# 全域音效資源
shoot_sound = None
explosion_sound = None
gamestart_music_path = None # Renamed from start_sound for clarity, path stored
boss_shoot_sound = None
enemy_shoot_sound = None # For general enemy shooting, or specific like Boss's scatter

def load_all_images():
    global background_img, player_img, enemy_img, elite_enemy_img
    global boss_lv1_img, boss_lv1_orange_img, boss_lv1_red_img, boss_lv1_yellow_img
    global player_bullet_img, enemy_bullet_img, boss_bullet_img

    try:
        background_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "space_bg.png")).convert()
        print(f"DEBUG: background_img loaded: {background_img}")
    except Exception as e:
        print(f"載入背景圖片失敗: {e}")
        background_img = None

    try:
        player_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "space_cat.png")).convert_alpha()
        print(f"DEBUG: player_img loaded: {player_img}")
    except Exception as e:
        print(f"載入主角圖片失敗: {e}")
        player_img = None

    try:
        enemy_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "alien.png")).convert_alpha()
        print(f"DEBUG: enemy_img loaded: {enemy_img}")
    except Exception as e:
        print(f"載入敵人圖片失敗: {e}")
        enemy_img = None

    try:
        elite_enemy_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "elite_alien.png")).convert_alpha()
        print(f"DEBUG: elite_enemy_img loaded: {elite_enemy_img}")
    except Exception as e:
        print(f"載入菁英敵人圖片失敗: {e}")
        elite_enemy_img = None

    try:
        boss_lv1_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "boss_Lv1.png")).convert_alpha()
        print(f"DEBUG: boss_lv1_img loaded: {boss_lv1_img}")
    except Exception as e:
        print(f"載入Boss Lv1圖片失敗: {e}")
        boss_lv1_img = None

    try:
        boss_lv1_orange_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "boss_Lv1_orange_tinted.png")).convert_alpha()
        print(f"DEBUG: boss_lv1_orange_img loaded: {boss_lv1_orange_img}")
    except Exception as e:
        print(f"載入Boss Lv1橘色圖片失敗: {e}")
        boss_lv1_orange_img = None

    try:
        boss_lv1_red_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "boss_Lv1_red_tinted.png")).convert_alpha()
        print(f"DEBUG: boss_lv1_red_img loaded: {boss_lv1_red_img}")
    except Exception as e:
        print(f"載入Boss Lv1紅色圖片失敗: {e}")
        boss_lv1_red_img = None

    try:
        boss_lv1_yellow_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "boss_Lv1_yellow_tinted.png")).convert_alpha()
        print(f"DEBUG: boss_lv1_yellow_img loaded: {boss_lv1_yellow_img}")
    except Exception as e:
        print(f"載入Boss Lv1黃色圖片失敗: {e}")
        boss_lv1_yellow_img = None

    try:
        player_bullet_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "player_bullet.png")).convert_alpha()
        print(f"DEBUG: player_bullet_img loaded: {player_bullet_img}")
    except Exception as e:
        print(f"載入主角子彈圖片失敗: {e}")
        player_bullet_img = None

    try:
        enemy_bullet_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "cocoa_bullet.png")).convert_alpha()
        print(f"DEBUG: enemy_bullet_img loaded: {enemy_bullet_img}")
    except Exception as e:
        print(f"載入敵人子彈圖片失敗: {e}")
        enemy_bullet_img = None

    try:
        boss_bullet_img = pygame.image.load(os.path.join(BASE_DIR, IMAGE_DIR, "Blazing_Starshot.png")).convert_alpha()
        print(f"DEBUG: boss_bullet_img loaded: {boss_bullet_img}")
    except Exception as e:
        print(f"載入Boss子彈圖片失敗: {e}")
        boss_bullet_img = None

def load_all_sounds():
    global shoot_sound, explosion_sound, gamestart_music_path, boss_shoot_sound, enemy_shoot_sound
    try:
        shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, SOUND_DIR, "shoot.wav"))
        print(f"DEBUG: shoot_sound loaded: {shoot_sound}")
    except Exception as e:
        print(f"載入射擊音效失敗: {e}")
        shoot_sound = None
    try:
        explosion_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, SOUND_DIR, "explosion.wav"))
        print(f"DEBUG: explosion_sound loaded: {explosion_sound}")
    except Exception as e:
        print(f"載入爆炸音效失敗: {e}")
        explosion_sound = None
    # gamestart.mp3 只記錄路徑，不用 Sound 物件
    gamestart_music_path = os.path.join(BASE_DIR, SOUND_DIR, "gamestart.mp3")
    if not os.path.exists(gamestart_music_path):
        print(f"載入開始音樂失敗: 找不到 {gamestart_music_path}")
        gamestart_music_path = None
    else:
        print(f"DEBUG: gamestart_music_path loaded: {gamestart_music_path}")
    try:
        boss_shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, SOUND_DIR, "boss_shoot.wav")) # Assumed filename
        print(f"DEBUG: boss_shoot_sound loaded: {boss_shoot_sound}")
    except Exception as e:
        print(f"載入Boss射擊音效失敗 (boss_shoot.wav): {e}")
        boss_shoot_sound = None
    try:
        # This sound is used by Boss Lv1 for its scatter attack.
        # You might want a more generic enemy_shoot.wav or a specific one like scatter_shoot.wav
        enemy_shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, SOUND_DIR, "enemy_shoot.wav")) # Assumed filename
        print(f"DEBUG: enemy_shoot_sound (for scatter) loaded: {enemy_shoot_sound}")
    except Exception as e:
        print(f"載入敵人/散彈射擊音效失敗 (enemy_shoot.wav): {e}")
        enemy_shoot_sound = None

def load_fonts():
    fonts = {}
    try:
        fonts['chinese_font'] = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "NotoSansCJKtc-Regular.otf"), 28)
        fonts['title_font'] = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "NotoSansCJKtc-Bold.otf"), 48)
        fonts['small_font'] = pygame.font.Font(os.path.join(BASE_DIR, "fonts", "NotoSansCJKtc-Regular.otf"), 18)
        print("成功載入自訂中文字體")
    except Exception as e:
        print(f"載入自訂字型失敗: {e}")
        try:
            fonts['chinese_font'] = pygame.font.SysFont("microsoftjhenghei", 28)
            fonts['title_font'] = pygame.font.SysFont("microsoftjhenghei", 48)
            fonts['small_font'] = pygame.font.SysFont("microsoftjhenghei", 18)
            print("成功載入系統中文字體: microsoftjhenghei")
        except Exception as e2:
            print(f"載入系統中文字體失敗: {e2}")
            fonts['chinese_font'] = pygame.font.SysFont(None, 28)
            fonts['title_font'] = pygame.font.SysFont(None, 48)
            fonts['small_font'] = pygame.font.SysFont(None, 18)
            print("已使用 pygame 預設字體作為備援")
    return fonts

def play_sound(sound):
    if sound:
        try:
            sound.play()
        except Exception as e:
            print(f"播放音效時發生錯誤: {e}")

def play_gamestart_music():
    if gamestart_music_path:
        try:
            pygame.mixer.music.load(gamestart_music_path)
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"播放開始音樂時發生錯誤: {e}")
    else:
        print("[警告] 無法播放開始音樂，gamestart.mp3 未載入。")

def init_resources():
    load_all_images()
    load_all_sounds()
    fonts = load_fonts()
    return fonts