import pygame
import os

# --- 常數定義 ---
# 假設此檔案 (animated_sunflower.py) 位於 entities 資料夾下
# PROJECT_ROOT 應該是 d:\coding\tower_defense_game
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPRITE_SHEET_PATH_SUNFLOWER = os.path.join(PROJECT_ROOT, "assets", "images", "sunflower.png")
FRAME_WIDTH = 80  # Updated frame width for animations
FRAME_HEIGHT = 80 # Updated frame height for animations
ANIMATION_HORIZONTAL_SPACING = 4 # New: Horizontal spacing between animation frames
COLOR_KEY_SUNFLOWER = (185, 124, 191) # 更新後的紫色背景

# 動畫狀態設定
# 格式: "state_name": {"start_coord": (x, y), "frames_count": count, "duration_ms": frame_duration, "loop": True/False}
ANIMATION_STATES_CONFIG = {
    "idle": {"start_coord": (10, 52), "frames_count": 6, "duration_ms": 120, "loop": True},
    "glow": {"start_coord": (10, 170), "frames_count": 3, "duration_ms": 80, "loop": False}, # Glow is now non-looping
}
DEFAULT_ANIMATION_STATE = "idle"

# 靜態圖像座標和大小
SEED_PACKET_COORD = (278, 170)
SEED_PACKET_WIDTH = 49
SEED_PACKET_HEIGHT = 69

SUN_ICON_COORD = (391, 170)
SUN_ICON_WIDTH = 48
SUN_ICON_HEIGHT = 48

# Note: STATIC_IMAGE_WIDTH and STATIC_IMAGE_HEIGHT are now specific to each static image


class AnimatedSunflower(pygame.sprite.Sprite):
    def __init__(self, position=(0, 0)):
        super().__init__()
        self.animations = {}  # 格式: {"state_name": {"frames": [], "duration_ms": ms, "loop": bool}}
        self._load_animations()

        self.current_state = DEFAULT_ANIMATION_STATE
        self.current_animation_frames = []
        self.current_animation_duration_ms = 0
        self.current_animation_loop = True
        
        self.current_frame_index = 0
        self.last_frame_update_time = pygame.time.get_ticks()

        self._set_current_animation_by_state(self.current_state) # 初始化第一個動畫

        if not self.current_animation_frames:
            print(f"警告：AnimatedSunflower 初始化時 '{self.current_state}' 狀態沒有可用的動畫幀。")
            self.image = pygame.Surface([FRAME_WIDTH, FRAME_HEIGHT], pygame.SRCALPHA)
            self.image.fill((255, 255, 0, 100)) # 半透明黃色預留位置
        else:
            self.image = self.current_animation_frames[self.current_frame_index]
        
        self.rect = self.image.get_rect(center=position)

    def _load_animations(self):
        """載入並解析 Sprite Sheet 以建立動畫。"""
        try:
            sprite_sheet_image = pygame.image.load(SPRITE_SHEET_PATH_SUNFLOWER).convert()
            sprite_sheet_image.set_colorkey(COLOR_KEY_SUNFLOWER) # 設定透明色
        except pygame.error as e:
            print(f"錯誤：無法載入 Sunflower Sprite Sheet '{SPRITE_SHEET_PATH_SUNFLOWER}': {e}")
            return

        for state_name, config in ANIMATION_STATES_CONFIG.items():
            frames = []
            start_x, start_y = config["start_coord"]
            for i in range(config["frames_count"]):
                # Apply horizontal spacing for subsequent frames
                x = start_x + (i * (FRAME_WIDTH + ANIMATION_HORIZONTAL_SPACING)) 
                frame_rect = pygame.Rect(x, start_y, FRAME_WIDTH, FRAME_HEIGHT)
                # print(f"Cutting {state_name} frame {i} at {frame_rect}") # Debug print
                frame_surface = sprite_sheet_image.subsurface(frame_rect)
                frames.append(frame_surface)
            
            self.animations[state_name] = {
                "frames": frames, 
                "duration_ms": config["duration_ms"],
                "loop": config.get("loop", True) # 預設循環播放
            }
        
        # 載入靜態圖像
        try:
            self.seed_packet_image = sprite_sheet_image.subsurface(
                pygame.Rect(SEED_PACKET_COORD[0], SEED_PACKET_COORD[1], SEED_PACKET_WIDTH, SEED_PACKET_HEIGHT)
            )
        except ValueError as e: # pygame.Rect might be out of bounds
            print(f"錯誤：無法切割 Seed Packet 圖像於 {SEED_PACKET_COORD}: {e}")
            self.seed_packet_image = pygame.Surface((SEED_PACKET_WIDTH, SEED_PACKET_HEIGHT), pygame.SRCALPHA)
            self.seed_packet_image.fill((200,150,50, 128)) # 半透明棕色預留

        try:
            self.sun_icon_image = sprite_sheet_image.subsurface(
                pygame.Rect(SUN_ICON_COORD[0], SUN_ICON_COORD[1], SUN_ICON_WIDTH, SUN_ICON_HEIGHT)
            )
        except ValueError as e:
            print(f"錯誤：無法切割 Sun Icon 圖像於 {SUN_ICON_COORD}: {e}")
            self.sun_icon_image = pygame.Surface((SUN_ICON_WIDTH, SUN_ICON_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(self.sun_icon_image, (255,223,0, 128), (SUN_ICON_WIDTH//2, SUN_ICON_HEIGHT//2), SUN_ICON_WIDTH//2)

        print(f"成功載入 Sunflower 的 {len(self.animations)} 種動畫狀態。")

    def _set_current_animation_by_state(self, state_name):
        """根據狀態名稱設定當前播放的動畫。"""
        animation_data = self.animations.get(state_name)
        if not animation_data:
            print(f"警告：找不到動畫狀態 '{state_name}'。嘗試退回至 '{DEFAULT_ANIMATION_STATE}'。")
            animation_data = self.animations.get(DEFAULT_ANIMATION_STATE)
            if not animation_data:
                print(f"錯誤：連預設動畫狀態 '{DEFAULT_ANIMATION_STATE}' 都找不到！")
                self.current_animation_frames = []
                return
            else:
                self.current_state = DEFAULT_ANIMATION_STATE # 更新為實際使用的狀態

        self.current_animation_frames = animation_data["frames"]
        self.current_animation_duration_ms = animation_data["duration_ms"]
        self.current_animation_loop = animation_data["loop"]
        self.current_frame_index = 0 
        self.last_frame_update_time = pygame.time.get_ticks()
        
        if self.current_animation_frames:
            self.image = self.current_animation_frames[self.current_frame_index]
        else: # 如果選中的動畫沒有影格
             print(f"警告：狀態 '{self.current_state}' 沒有動畫影格。")
             self.image = pygame.Surface([FRAME_WIDTH, FRAME_HEIGHT], pygame.SRCALPHA) # 透明預留
             self.image.fill((0,0,0,0))


    def set_state(self, state_name):
        """設定角色的動畫狀態 (例如 'idle', 'glow')。"""
        if state_name not in self.animations:
            print(f"警告：動畫狀態 '{state_name}' 不存在。可用的狀態有：{list(self.animations.keys())}")
            return
        if self.current_state != state_name or self.current_frame_index != 0: # 也允許重播相同狀態
            print(f"設定 Sunflower 動畫狀態為: {state_name}")
            self.current_state = state_name
            self._set_current_animation_by_state(state_name)

    def update(self):
        """更新動畫影格。"""
        print(f"[DEBUG AnimatedSunflower ID: {id(self)}] Update called. Current state: {self.current_state}, Frame: {self.current_frame_index}") # DEBUG
        if not self.current_animation_frames or self.current_animation_duration_ms <= 0:
            return


        now = pygame.time.get_ticks()
        time_since_last_frame_update = now - self.last_frame_update_time
        print(f"[DEBUG AnimSF ID: {id(self)}] Time check: now={now}, last_update={self.last_frame_update_time}, diff={time_since_last_frame_update}, duration_needed={self.current_animation_duration_ms}, current_frame={self.current_frame_index}") # Detailed time check
        if time_since_last_frame_update > self.current_animation_duration_ms:
            self.last_frame_update_time = now
            
            if self.current_frame_index < len(self.current_animation_frames) - 1:
                self.current_frame_index += 1
            elif self.current_animation_loop:
                self.current_frame_index = 0
            elif not self.current_animation_loop: # Animation finished and not looping
                # If the current state is "glow" and it finished, revert to "idle"
                if self.current_state == "glow": # Check if it was "glow"
                    self.set_state(DEFAULT_ANIMATION_STATE) # Revert to idle
            
            self.image = self.current_animation_frames[self.current_frame_index]

    def draw(self, screen):
        """將目前影格繪製到螢幕上。"""
        print(f"[DEBUG AnimatedSunflower.draw] rect.center={self.rect.center}, image size={self.image.get_size()}")
        screen.blit(self.image, self.rect)

    def draw_seed_packet(self, screen, position):
        """繪製種子包圖示 (可選)。"""
        if self.seed_packet_image:
            screen.blit(self.seed_packet_image, position)
            
    def draw_sun_icon(self, screen, position):
        """繪製太陽圖示 (可選)。"""
        if self.sun_icon_image:
            screen.blit(self.sun_icon_image, position)

# --- 主迴圈 (用於展示) ---
def main_demo():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("AnimatedSunflower 展示")
    clock = pygame.time.Clock()

    sunflower = AnimatedSunflower(position=(screen_width // 2, screen_height // 2))
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(sunflower)

    running = True
    font = pygame.font.SysFont("Arial", 24)

    print("-" * 30)
    print("Sunflower 動畫展示控制：")
    print("  I 鍵：切換到 Idle 狀態")
    print("  G 鍵：切換到 Glow 狀態")
    print("  ESC 鍵：離開")
    print("-" * 30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_i:
                    sunflower.set_state("idle")
                if event.key == pygame.K_g:
                    sunflower.set_state("glow")

        all_sprites.update() 

        screen.fill((50, 50, 50))  # 深灰色背景
        all_sprites.draw(screen)

        # 繪製 UI 元素範例
        sunflower.draw_seed_packet(screen, (screen_width - 50, 10))
        sunflower.draw_sun_icon(screen, (screen_width - 50, 50))
        
        info_text = font.render(f"狀態 (I/G): {sunflower.current_state}", True, (255, 255, 255))
        screen.blit(info_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    # 確保 PROJECT_ROOT 和 SPRITE_SHEET_PATH_SUNFLOWER 正確
    print(f"PROJECT_ROOT 設定為: {PROJECT_ROOT}")
    print(f"正在從以下路徑載入 Sunflower Sprite Sheet: {SPRITE_SHEET_PATH_SUNFLOWER}")
    main_demo()
