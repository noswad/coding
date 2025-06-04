import pygame
import os

# --- 常數定義 ---
# 取得專案根目錄 (d:\coding\tower_defense_game)
# __file__ 現在是 d:\coding\tower_defense_game\entities\animated_peashooter.py
# os.path.dirname(os.path.abspath(__file__)) 是 d:\coding\tower_defense_game\entities
# os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 是 d:\coding\tower_defense_game
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPRITE_SHEET_FILENAME = "peashooter_sprite.png" # All peashooter types are on this sheet
SPRITE_SHEET_PATH = os.path.join(PROJECT_ROOT, "assets", "images", SPRITE_SHEET_FILENAME)
FRAME_WIDTH = 80
FRAME_HEIGHT = 80
ANIMATION_HORIZONTAL_SPACING = 4
COLOR_KEY = (185, 124, 191) # 紫色背景

# 植物類型和其資產的設定
PLANT_DATA_CONFIG = {
    "Peashooter": {
        "animations": {
            "Idle": {"start_coord": (10, 52), "frames_count": 6, "duration_ms": 150, "loop": True},
            "Attack": {"start_coord": (10, 170), "frames_count": 3, "duration_ms": 80, "loop": False},
        },
        "static_images": {
            "seed_packet": {"coord": (311, 170), "size": (49, 69)},
            "pea": {"coord": (266, 170), "size": (19, 18)},
        }
    },
    "SnowPea": {
        "animations": {
            "Idle": {"start_coord": (10, 312), "frames_count": 6, "duration_ms": 150, "loop": True},
            "Attack": {"start_coord": (10, 430), "frames_count": 3, "duration_ms": 80, "loop": False},
        },
        "static_images": {
            "seed_packet": {"coord": (356, 430), "size": (49, 69)},
            "pea": {"coord": (266, 430), "size": (19, 18)},
            "improved_pea": {"coord": (266, 470), "size": (22, 18)},
        }
    },
    "RepeaterPea": {
        "animations": {
            "Idle": {"start_coord": (10, 618), "frames_count": 6, "duration_ms": 150, "loop": True},
            "Attack": {"start_coord": (10, 740), "frames_count": 3, "duration_ms": 80, "loop": False},
        },
        "static_images": {
            "seed_packet": {"coord": (278, 740), "size": (49, 69)},
            "pea": {"coord": (266, 170), "size": (19, 18)}, # Uses Peashooter's pea coord/size
        }
    },
    "GatlingPea": {
        "animations": {
            "Idle": {"start_coord": (10, 876), "frames_count": 6, "duration_ms": 150, "loop": True},
            "Attack": {"start_coord": (10, 994), "frames_count": 3, "duration_ms": 80, "loop": False},
        },
        "static_images": {
            "seed_packet": {"coord": (270, 994), "size": (49, 69)},
            # 更新 FIRE PEA 座標
            "fire_pea": {"coord": (391, 994), "size": (36, 18)},
        }
    }
}

# 可用的造型和動作 (用於驗證和預設值)
AVAILABLE_PLANT_TYPES = list(PLANT_DATA_CONFIG.keys())
# Assuming "Idle" and "Attack" are the common actions. This can be made more dynamic if needed.
AVAILABLE_ACTIONS = ["Idle", "Attack"]
DEFAULT_PLANT_TYPE = "Peashooter"
DEFAULT_ACTION = "Idle"


class Peashooter(pygame.sprite.Sprite):
    def __init__(self, plant_type=DEFAULT_PLANT_TYPE, position=(0, 0)):
        super().__init__()
        
        self.plant_type = plant_type
        self.current_action = DEFAULT_ACTION

        # These will store assets for the current plant_type
        self.animations_for_current_type = {}  # {"ActionName": {"frames": [], "duration_ms": ms, "loop": bool}}
        self.static_images_for_current_type = {} # {"image_name": surface}

        self._sprite_sheet_surface = None # To store the loaded sprite sheet
        self._load_sprite_sheet()

        if self._sprite_sheet_surface:
            self._load_assets_for_plant_type()
        else:
            print(f"錯誤: Sprite sheet 未載入，無法為 {self.plant_type} 載入資產。")

        self.current_animation_frames = []
        self.current_animation_duration_ms = 0
        self.current_animation_loop = True

        self.current_frame_index = 0
        self.last_frame_update_time = pygame.time.get_ticks()

        self._set_current_animation_by_action(self.current_action) # 初始化第一個動畫

        if not self.current_animation_frames:
            print(f"警告：植物 '{self.plant_type}' 的動作 '{self.current_action}' 初始化時沒有可用的動畫幀。將使用預留位置。")
            self.image = pygame.Surface([FRAME_WIDTH, FRAME_HEIGHT], pygame.SRCALPHA)
            self.image.fill((255, 0, 255, 255)) # 改為不透明的亮洋紅色以供調試
        else:
            self.image = self.current_animation_frames[self.current_frame_index]
        
        self.rect = self.image.get_rect(center=position)

    def _load_sprite_sheet(self):
        """載入主 Sprite Sheet。"""
        try:
            self._sprite_sheet_surface = pygame.image.load(SPRITE_SHEET_PATH).convert()
            self._sprite_sheet_surface.set_colorkey(COLOR_KEY) # 設定透明色
        except pygame.error as e:
            print(f"錯誤：無法載入 Sprite Sheet '{SPRITE_SHEET_PATH}': {e}")
            self._sprite_sheet_surface = None

    def _load_assets_for_plant_type(self):
        """為目前的 plant_type 載入動畫和靜態圖像。"""
        if not self._sprite_sheet_surface:
            print(f"錯誤: Sprite sheet 未載入，無法為 {self.plant_type} 載入資產。")
            return

        self.animations_for_current_type = {}
        self.static_images_for_current_type = {}

        plant_config = PLANT_DATA_CONFIG.get(self.plant_type)
        if not plant_config:
            print(f"錯誤：在 PLANT_DATA_CONFIG 中找不到植物類型 '{self.plant_type}' 的設定。")
            return

        # 載入動畫
        for anim_name, anim_config in plant_config.get("animations", {}).items():
            frames = []
            start_x_anim, start_y_anim = anim_config["start_coord"]
            for i in range(anim_config["frames_count"]):
                x = start_x_anim + (i * (FRAME_WIDTH + ANIMATION_HORIZONTAL_SPACING))
                y = start_y_anim
                try:
                    frame_surface = self._sprite_sheet_surface.subsurface(pygame.Rect(x, y, FRAME_WIDTH, FRAME_HEIGHT))
                    frames.append(frame_surface)
                except ValueError as e:
                    print(f"錯誤：切割動畫幀 '{self.plant_type}'-'{anim_name}' 索引 {i} 於 ({x},{y}) 失敗: {e}")
                    # Add a placeholder frame if cutting fails
                    placeholder_frame = pygame.Surface([FRAME_WIDTH, FRAME_HEIGHT], pygame.SRCALPHA)
                    placeholder_frame.fill((255,0,0,100)) # Semi-transparent red
                    frames.append(placeholder_frame)

            self.animations_for_current_type[anim_name] = {
                "frames": frames,
                "duration_ms": anim_config["duration_ms"],
                "loop": anim_config.get("loop", True)
            }

        # 載入靜態圖像
        for img_name, img_config in plant_config.get("static_images", {}).items():
            coord = img_config["coord"]
            size = img_config["size"]
            try:
                static_surface = self._sprite_sheet_surface.subsurface(pygame.Rect(coord[0], coord[1], size[0], size[1]))
                self.static_images_for_current_type[img_name] = static_surface
            except ValueError as e:
                print(f"錯誤：切割靜態圖像 '{self.plant_type}'-'{img_name}' 於 {coord} 失敗: {e}")
                placeholder_static = pygame.Surface(size, pygame.SRCALPHA)
                placeholder_static.fill((0,0,255,100)) # Semi-transparent blue
                self.static_images_for_current_type[img_name] = placeholder_static
        
        print(f"成功為植物類型 '{self.plant_type}' 載入 {len(self.animations_for_current_type)} 種動畫和 {len(self.static_images_for_current_type)} 個靜態圖像。")

    def _set_current_animation_by_action(self, action_name):
        """根據動作名稱設定當前播放的動畫。"""
        animation_data = self.animations_for_current_type.get(action_name)
        if not animation_data:
            print(f"警告：植物類型 '{self.plant_type}' 找不到動作 '{action_name}'。嘗試退回至 '{DEFAULT_ACTION}'。")
            animation_data = self.animations_for_current_type.get(DEFAULT_ACTION)
            if not animation_data:
                print(f"錯誤：植物類型 '{self.plant_type}' 連預設動作 '{DEFAULT_ACTION}' 都找不到！")
                self.current_animation_frames = []
                self.current_animation_duration_ms = 0
                self.current_animation_loop = True
                return
            else:
                self.current_action = DEFAULT_ACTION # 更新為實際使用的動作名稱

        self.current_animation_frames = animation_data["frames"]
        self.current_animation_duration_ms = animation_data["duration_ms"]
        self.current_animation_loop = animation_data["loop"]
        self.current_frame_index = 0 
        self.last_frame_update_time = pygame.time.get_ticks()
        
        if self.current_animation_frames:
            self.image = self.current_animation_frames[self.current_frame_index]
        else:
             print(f"警告：植物 '{self.plant_type}' 的動作 '{self.current_action}' 沒有動畫影格。")
             self.image = pygame.Surface([FRAME_WIDTH, FRAME_HEIGHT], pygame.SRCALPHA)
             self.image.fill((255, 0, 255, 255)) # 改為不透明的亮洋紅色以供調試

    def set_plant_type(self, plant_type_name):
        """設定植物的類型 (例如 "Peashooter", "SnowPea")。"""
        if plant_type_name not in AVAILABLE_PLANT_TYPES:
            print(f"警告：植物類型 '{plant_type_name}' 不可用。可用的類型有：{AVAILABLE_PLANT_TYPES}")
            return
        if self.plant_type != plant_type_name:
            print(f"設定植物類型為: {plant_type_name}")
            self.plant_type = plant_type_name
            if self._sprite_sheet_surface:
                self._load_assets_for_plant_type() # 重新載入該類型的資產
            self.current_action = DEFAULT_ACTION # 重設為預設動作
            self._set_current_animation_by_action(self.current_action)

    def set_action(self, action_name):
        """設定角色的動畫動作 (例如 Idle, Attack)。"""
        if action_name not in AVAILABLE_ACTIONS:
            print(f"警告：動作 '{action_name}' 不可用。可用的動作有：{AVAILABLE_ACTIONS}")
            return
        if self.current_action != action_name:
            print(f"設定植物 '{self.plant_type}' 的動作為: {action_name}")
            self.current_action = action_name
            self._set_current_animation_by_action(action_name)

    def update(self):
        """更新動畫影格。"""
        if not self.current_animation_frames or self.current_animation_duration_ms <= 0:
            return # 沒有動畫可播放或影格時間無效

        now = pygame.time.get_ticks()
        if now - self.last_frame_update_time > self.current_animation_duration_ms:
            self.last_frame_update_time = now
            
            if self.current_frame_index < len(self.current_animation_frames) - 1:
                self.current_frame_index += 1
            elif self.current_animation_loop:
                self.current_frame_index = 0
            # 如果不是循環且已到達最後一幀，則停在最後一幀
            elif not self.current_animation_loop: # Animation finished and not looping
                # If the current action is "Attack" and it finished, revert to "Idle" (DEFAULT_ACTION)
                if self.current_action == "Attack" and self.current_action != DEFAULT_ACTION:
                    self.set_action(DEFAULT_ACTION)
            
            self.image = self.current_animation_frames[self.current_frame_index]

    def draw(self, screen):
        """將目前影格繪製到螢幕上。"""
        screen.blit(self.image, self.rect)

    def get_static_image(self, image_name):
        """取得指定的靜態圖像 Surface。"""
        return self.static_images_for_current_type.get(image_name)


# --- 主迴圈 (用於展示) ---
def main_loop():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Peashooter 動畫展示")
    clock = pygame.time.Clock()

    # 將豌豆射手放在畫面中央
    plant_entity = Peashooter(plant_type=DEFAULT_PLANT_TYPE, position=(screen_width // 2, screen_height // 2))
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(plant_entity)

    running = True
    current_plant_type_index = AVAILABLE_PLANT_TYPES.index(DEFAULT_PLANT_TYPE)
    current_action_index = 0
    
    # 字型用於顯示資訊
    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)

    print("-" * 30)
    print("控制方式：")
    print("  T 鍵：切換植物類型 (Type)")
    print("  A 鍵：切換動作 (Action)")
    print("  ESC 鍵：離開")
    print("-" * 30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_t: # 切換植物類型
                    current_plant_type_index = (current_plant_type_index + 1) % len(AVAILABLE_PLANT_TYPES)
                    plant_entity.set_plant_type(AVAILABLE_PLANT_TYPES[current_plant_type_index])
                if event.key == pygame.K_a: # 切換動作
                    current_action_index = (current_action_index + 1) % len(AVAILABLE_ACTIONS)
                    plant_entity.set_action(AVAILABLE_ACTIONS[current_action_index])

        all_sprites.update() # 更新 Peashooter 的動畫

        screen.fill((30, 30, 30))  # 深灰色背景
        all_sprites.draw(screen)   # 繪製 Peashooter

        # 繪製靜態圖像 (種子包和豆子)
        seed_packet_img = plant_entity.get_static_image("seed_packet")
        if seed_packet_img:
            screen.blit(seed_packet_img, (screen_width - seed_packet_img.get_width() - 10, 10))
            text_surf = small_font.render("Seed", True, (200,200,200))
            screen.blit(text_surf, (screen_width - seed_packet_img.get_width() - 10, 10 + seed_packet_img.get_height()))


        pea_img_name = "pea" # Default pea name
        if plant_entity.plant_type == "GatlingPea":
            pea_img_name = "fire_pea"
        elif plant_entity.plant_type == "SnowPea":
            # SnowPea has "pea" and "improved_pea", let's show "pea" for now
            pea_img_name = "pea" 
            
        pea_img = plant_entity.get_static_image(pea_img_name)
        y_offset_for_pea = 10 + (seed_packet_img.get_height() if seed_packet_img else 0) + 20

        if pea_img:
            screen.blit(pea_img, (screen_width - pea_img.get_width() - 10, y_offset_for_pea))
            text_surf = small_font.render(pea_img_name.capitalize(), True, (200,200,200))
            screen.blit(text_surf, (screen_width - pea_img.get_width() - 10, y_offset_for_pea + pea_img.get_height()))
        
        if plant_entity.plant_type == "SnowPea":
            improved_pea_img = plant_entity.get_static_image("improved_pea")
            if improved_pea_img:
                y_offset_for_improved_pea = y_offset_for_pea + (pea_img.get_height() if pea_img else 0) + 20
                screen.blit(improved_pea_img, (screen_width - improved_pea_img.get_width() - 10, y_offset_for_improved_pea ))
                text_surf = small_font.render("Improved Pea", True, (200,200,200))
                screen.blit(text_surf, (screen_width - improved_pea_img.get_width() - 10, y_offset_for_improved_pea + improved_pea_img.get_height()))

        # 顯示目前狀態
        info_text_type = font.render(f"類型 (T): {plant_entity.plant_type}", True, (255, 255, 255))
        info_text_action = font.render(f"動作 (A): {plant_entity.current_action}", True, (255, 255, 255))
        screen.blit(info_text_type, (10, 10))
        screen.blit(info_text_action, (10, 50))

        pygame.display.flip()
        clock.tick(60)  # FPS

    pygame.quit()


if __name__ == "__main__":
    # PROJECT_ROOT 已在檔案頂部根據此檔案的新位置進行了調整。
    print(f"PROJECT_ROOT 設定為: {PROJECT_ROOT}")
    print(f"正在從以下路徑載入 Sprite Sheet: {SPRITE_SHEET_PATH}")
    main_loop()
