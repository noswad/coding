# game_view.py
import pygame
import os # Needed for path joining
# 假設 config.py 可被存取，例如，如果 game_view.py 與執行 main.py 的腳本在同一目錄中，
# 或者 config 的值是透過 game_logic.config 傳遞的。
# 在此範例中，我假設 config 的值是透過 game_logic.config 存取的。

# 如果未載入資產，則使用預留位置顏色
PLACEHOLDER_GREEN = (0, 180, 0)
PLACEHOLDER_BROWN = (139, 69, 19)
PLACEHOLDER_YELLOW = (255, 223, 0)
PLACEHOLDER_BLUE = (0, 0, 200)
PLACEHOLDER_GREY = (128, 128, 128)
PLACEHOLDER_DARK_GREY = (50, 50, 50)
PLACEHOLDER_RED = (200, 0, 0)
PLACEHOLDER_LIGHT_BLUE = (173, 216, 230)

# UI 常數 (可以移至設定檔或主題檔案)
CARD_BAR_HEIGHT = 130
CARD_WIDTH = 70 # UI 中植物卡片的寬度
CARD_HEIGHT = 100 # UI 中植物卡片的高度
CARD_PADDING = 10
SUN_COUNT_X_OFFSET = 20
SUN_COUNT_Y_OFFSET = 20
SHOVEL_BUTTON_SIZE = 60
SHOVEL_BUTTON_PADDING = 10 # 鏟子按鈕與螢幕邊緣的間距

GRID_LINE_COLOR = (50, 50, 50, 100) # 格線的半透明深灰色
PLANT_MARKER_COLOR = (0, 255, 0, 50) # 植物放置標記的半透明綠色
INVALID_PLANT_MARKER_COLOR = (255, 0, 0, 50) # 無效放置標記的半透明紅色

COOLDOWN_MASK_COLOR = (0, 0, 0, 150) # 冷卻遮罩的半透明黑色
SELECTED_CARD_BORDER_COLOR = (255, 255, 0, 200) # 選中卡片的黃色邊框
UNAVAILABLE_CARD_TINT_COLOR = (100, 100, 100, 100) # 無法使用卡片的暗色調

class GameView:
    """
    處理遊戲的所有渲染，包括背景、網格、實體、UI 和效果。
    """
    def __init__(self, screen, game_logic):
        """
        初始化 GameView。

        Args:
            screen:主要的 Pygame 顯示表面。
            game_logic:主要的遊戲邏輯控制器物件 (例如，您的 Game 類別的實例)。
                        此物件應提供對遊戲狀態和設定的存取。
        """
        self.screen = screen
        self.game = game_logic # 對遊戲邏輯的參考 (例如 Game 類別實例)
        self.config = game_logic.config # 存取設定值，如 CELL_WIDTH 等。

        # 從 main.py 取得螢幕尺寸 (可以傳遞或透過 game_logic 存取)
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # 網格尺寸和偏移量
        self.grid_rows = self.config.GRID_ROWS
        self.grid_cols = self.config.GRID_COLS
        self.cell_width = self.config.CELL_WIDTH
        self.cell_height = self.config.CELL_HEIGHT
        
        # 計算網格偏移量以容納頂部的卡片欄
        self.grid_offset_x = (self.screen_width - (self.grid_cols * self.cell_width)) // 2 # 水平置中網格
        self.grid_offset_y = CARD_BAR_HEIGHT

        # 載入資產 (最好透過資產管理器)
        self._load_assets()

        # 字型
        try:
            self.font_sun_count = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_card_cost = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_debug = pygame.font.SysFont("Arial", 16)
        except pygame.error as e:
            print(f"警告：找不到字型，將使用預設字型。錯誤：{e}")
            self.font_sun_count = pygame.font.Font(None, 36) # Pygame 預設字型
            self.font_card_cost = pygame.font.Font(None, 24)
            self.font_debug = pygame.font.Font(None, 20)

        # UI 元素 Rect (鏟子範例)
        # 鏟子按鈕放在右上角，卡片列下方一點或與陽光數量對齊
        self.shovel_button_rect = pygame.Rect(
            self.screen_width - SHOVEL_BUTTON_SIZE - SHOVEL_BUTTON_PADDING,
            (CARD_BAR_HEIGHT - SHOVEL_BUTTON_SIZE) // 2, # 垂直置中於卡片列
            SHOVEL_BUTTON_SIZE,
            SHOVEL_BUTTON_SIZE
        )
        self.card_rects = self._calculate_card_rects()

        # 用於自訂滑鼠指標的表面
        self.custom_cursor_surface = None
        self.default_cursor_visible = True

    def _load_assets(self):
        """
        載入或準備所有必要的視覺資產。
        在真實遊戲中，這會使用 pygame.image.load() 載入圖片。
        目前使用預留位置表面。
        """
        # 載入背景圖片
        try:
            # 使用 self.config (即 game_config 模組) 來存取 PROJECT_ROOT
            background_image_path = os.path.join(self.config.PROJECT_ROOT, "assets", "images", "background.png")
            self.background_image = pygame.image.load(background_image_path).convert()
            # 確保背景圖片符合螢幕大小
            self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
        except pygame.error as e:
            print(f"錯誤：無法載入背景圖片 '{background_image_path}': {e}")
            print("將使用預設的綠色背景。")
            self.background_image = pygame.Surface((self.screen_width, self.screen_height))
            self.background_image.fill((34, 139, 34)) # 草地的森林綠 (預留)

        # 動畫效果圖層的預留位置 (例如，表面列表或動畫物件)
        self.animated_effect_layers = [] 

        # 鏟子圖示
        self.shovel_icon = pygame.Surface((SHOVEL_BUTTON_SIZE, SHOVEL_BUTTON_SIZE), pygame.SRCALPHA)
        self.shovel_icon.fill(PLACEHOLDER_GREY)
        pygame.draw.rect(self.shovel_icon, PLACEHOLDER_DARK_GREY, self.shovel_icon.get_rect(), 3)
        # TODO: 載入實際的鏟子圖示。路徑範例：
        # shovel_icon_path = os.path.join(PROJECT_ROOT, "assets", "images", "shovel.png")
        # self.shovel_icon = pygame.image.load(shovel_icon_path).convert_alpha()
        
        self.shovel_icon_hover = pygame.Surface((SHOVEL_BUTTON_SIZE, SHOVEL_BUTTON_SIZE), pygame.SRCALPHA)
        self.shovel_icon_hover.fill(PLACEHOLDER_LIGHT_BLUE) # 懸停時使用較淺的灰色
        pygame.draw.rect(self.shovel_icon_hover, PLACEHOLDER_DARK_GREY, self.shovel_icon_hover.get_rect(), 3)
        # TODO: 載入實際的鏟子懸停圖示。路徑範例：
        # shovel_icon_hover_path = os.path.join(PROJECT_ROOT, "assets", "images", "shovel_hover.png")
        # self.shovel_icon_hover = pygame.image.load(shovel_icon_hover_path).convert_alpha()

        # UI 的太陽圖示
        self.sun_ui_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.sun_ui_icon, PLACEHOLDER_YELLOW, (15, 15), 15)
        # TODO: 載入 UI 的實際太陽圖示。路徑範例：
        # sun_ui_icon_path = os.path.join(PROJECT_ROOT, "assets", "images", "sun_icon.png")
        # self.sun_ui_icon = pygame.image.load(sun_ui_icon_path).convert_alpha()

    def _calculate_card_rects(self):
        """計算 UI 列中每個植物卡片的螢幕矩形。"""
        card_rects = []
        # 卡片從陽光數量右邊開始排列
        start_x = SUN_COUNT_X_OFFSET + self.sun_ui_icon.get_width() + self.font_sun_count.size("999")[0] + 20 # 陽光數量後的空間
        if hasattr(self.game, 'plant_cards'):
            for i in range(len(self.game.plant_cards)):
                rect = pygame.Rect(
                    start_x + i * (CARD_WIDTH + CARD_PADDING),
                    (CARD_BAR_HEIGHT - CARD_HEIGHT) // 2, # 在卡片列中垂直置中
                    CARD_WIDTH,
                    CARD_HEIGHT
                )
                card_rects.append(rect)
        return card_rects

    def draw_background(self):
        """載入草地背景圖並繪製至畫面底層。"""
        self.screen.blit(self.background_image, (0, 0))

        # 如果有動畫效果圖層，則繪製它們
        for layer in self.animated_effect_layers:
            # 假設 layer 是一個表面或具有 draw(screen) 方法的物件
            if hasattr(layer, 'draw'):
                layer.draw(self.screen)
            elif isinstance(layer, pygame.Surface):
                self.screen.blit(layer, (0,0)) # 或效果的特定座標

    def draw_grid(self):
        """繪製每個格子的格線以及可選的植物放置標記。"""
        is_placing_plant = self.game.selected_plant_card is not None and not self.game.shovel_selected

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_rect = pygame.Rect(
                    self.grid_offset_x + col * self.cell_width,
                    self.grid_offset_y + row * self.cell_height,
                    self.cell_width,
                    self.cell_height
                )
                # 繪製格子邊框
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, cell_rect, 1)

                # 如果處於放置模式，顯示可放置區域高亮
                if is_placing_plant:
                    # 檢查 Grid 物件中的格子是否可放置
                    if self.game.grid.can_place(row, col):
                        highlight_surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
                        highlight_surface.fill(PLANT_MARKER_COLOR)
                        self.screen.blit(highlight_surface, cell_rect.topleft)
                    # 可以選擇性地為已被佔用的格子顯示不同的高亮 (例如紅色)
                    # elif self.game.grid.cells[row][col].unit is not None:
                    #     highlight_surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
                    #     highlight_surface.fill(INVALID_PLANT_MARKER_COLOR)
                    #     self.screen.blit(highlight_surface, cell_rect.topleft)
                
    def draw_plants(self):
        """繪製網格上所有活動的植物。假設每個植物物件都有一個 `draw(screen)` 方法，用於處理其自身的外觀和動畫狀態 (例如，食人花咬合)。"""
        if hasattr(self.game, 'plants'):
            for plant_instance in self.game.plants:
                if hasattr(plant_instance, 'visual_component') and plant_instance.visual_component:
                    plant_instance.visual_component.rect.center = plant_instance.rect.center # 確保位置同步
                    plant_instance.visual_component.draw(self.screen) # 繪製動畫視覺
                else:
                    plant_instance.draw(self.screen) # 後備：繪製邏輯植物的圖像 (預留位置)

    def draw_enemies(self):
        """繪製網格上所有活動的敵人。假設每個敵人物件都有一個 `draw(screen)` 方法，用於處理其自身的動畫 (行走、被攻擊、死亡)。"""
        if hasattr(self.game, 'enemies'):
            for enemy in self.game.enemies:
                enemy.draw(self.screen) # 每個敵人處理自己的繪圖邏輯

    def draw_projectiles(self):
        """繪製所有活動的投射物。假設每個投射物物件都有一個 `draw(screen)` 方法，用於處理其外觀 (例如，普通子彈 vs. 帶有藍色殘影的冰彈)。"""
        if hasattr(self.game, 'projectiles'):
            for projectile in self.game.projectiles:
                projectile.draw(self.screen) # 投射物處理自己的繪圖

    def draw_suns(self):
        """繪製從空中飄下或由太陽花產出的陽光。假設每個陽光物件都有一個 `draw(screen)` 方法。"""
        # Suns are now managed by ResourceManager
        if hasattr(self.game, 'resource_manager'):
            self.game.resource_manager.draw(self.screen)

    def draw_ui(self):
        """
        繪製使用者介面元素：
        - 頂部卡片欄 (植物圖示、陽光價格)。冷卻時間由 draw_cooldowns 處理。
        - 目前陽光數值 (左上)。
        - 鏟子按鈕與滑鼠懸停效果。
        """
        # 繪製卡片欄背景 (可選，如果不是主背景的一部分)
        card_bar_bg_rect = pygame.Rect(0, 0, self.screen_width, CARD_BAR_HEIGHT)
        pygame.draw.rect(self.screen, PLACEHOLDER_BROWN, card_bar_bg_rect) # 範例顏色

        # 繪製植物卡片
        if hasattr(self.game, 'plant_cards') and self.card_rects: # 確保 card_rects 已初始化
            for i, card_data in enumerate(self.game.plant_cards):
                if i < len(self.card_rects): # 避免索引超出範圍
                    card_rect = self.card_rects[i]
                    
                    # 繪製卡片背景
                    base_card_color = PLACEHOLDER_GREY
                    pygame.draw.rect(self.screen, base_card_color, card_rect)
                    
                    # 繪製植物圖示 (來自 PlantCard.icon_surface)
                    if card_data.icon_surface:
                        # 稍微調整圖示大小以適應卡片，並留出空間給價格
                        icon_width = card_rect.width - 10
                        icon_height = card_rect.height - 25 # 為價格留出底部空間
                        icon_scaled = pygame.transform.scale(card_data.icon_surface, (icon_width, icon_height))
                        self.screen.blit(icon_scaled, (card_rect.x + 5, card_rect.y + 5))
                    else: # 如果沒有圖示，繪製預留位置
                        icon_placeholder_rect = pygame.Rect(card_rect.x + 5, card_rect.y + 5, card_rect.width - 10, card_rect.height - 30)
                        pygame.draw.rect(self.screen, PLACEHOLDER_GREEN, icon_placeholder_rect)

                    # 繪製陽光價格
                    cost_text = self.font_card_cost.render(str(card_data.cost), True, PLACEHOLDER_YELLOW)
                    cost_pos_x = card_rect.centerx - cost_text.get_width() // 2
                    cost_pos_y = card_rect.bottom - cost_text.get_height() - 5
                    self.screen.blit(cost_text, (cost_pos_x, cost_pos_y))

                    # 如果卡片無法選取 (不夠陽光或冷卻中)，加上暗色調
                    if hasattr(self.game, 'player_sun') and not card_data.can_be_selected(self.game.player_sun):
                        tint_surface = pygame.Surface(card_rect.size, pygame.SRCALPHA)
                        tint_surface.fill(UNAVAILABLE_CARD_TINT_COLOR)
                        self.screen.blit(tint_surface, card_rect.topleft)

                    # 繪製卡片邊框 (如果選中則高亮)
                    border_color = SELECTED_CARD_BORDER_COLOR if card_data.is_selected else PLACEHOLDER_DARK_GREY
                    pygame.draw.rect(self.screen, border_color, card_rect, 2)

        # 繪製目前陽光數量
        if hasattr(self.game, 'player_sun'):
            sun_text_surface = self.font_sun_count.render(str(self.game.player_sun), True, PLACEHOLDER_YELLOW)
            # 太陽圖示垂直置中於文字
            sun_icon_y = SUN_COUNT_Y_OFFSET + (sun_text_surface.get_height() - self.sun_ui_icon.get_height()) // 2
            self.screen.blit(self.sun_ui_icon, (SUN_COUNT_X_OFFSET, sun_icon_y))
            self.screen.blit(sun_text_surface, (SUN_COUNT_X_OFFSET + self.sun_ui_icon.get_width() + 5, SUN_COUNT_Y_OFFSET))

        # 繪製鏟子按鈕
        mouse_pos = pygame.mouse.get_pos()
        is_hovering_shovel = self.shovel_button_rect.collidepoint(mouse_pos)
        
        shovel_selected_visual = hasattr(self.game, 'shovel_selected') and self.game.shovel_selected
        current_shovel_icon = self.shovel_icon_hover if is_hovering_shovel or shovel_selected_visual else self.shovel_icon
        self.screen.blit(current_shovel_icon, self.shovel_button_rect.topleft)
        
        if shovel_selected_visual:
            pygame.draw.rect(self.screen, PLACEHOLDER_YELLOW, self.shovel_button_rect, 3) # 選中時的黃色邊框

    def draw_cooldowns(self):
        """在 UI 列的植物卡片上繪製冷卻遮罩。遮罩的高度與剩餘冷卻時間成正比。"""
        if hasattr(self.game, 'plant_cards') and self.card_rects:
            for i, card_data in enumerate(self.game.plant_cards):
                if i < len(self.card_rects): # 避免索引超出範圍
                    card_rect = self.card_rects[i]
                    cooldown_progress = card_data.get_cooldown_progress() # Progress from 1.0 (full) to 0.0 (ready)

                    if cooldown_progress > 0: # progress 從 1.0 (剛使用) 到 0.0 (準備就緒)
                        mask_height = int(card_rect.height * cooldown_progress)
                        cooldown_mask_surface = pygame.Surface((card_rect.width, mask_height), pygame.SRCALPHA)
                        cooldown_mask_surface.fill(COOLDOWN_MASK_COLOR)
                        # 從底部向上繪製遮罩
                        self.screen.blit(cooldown_mask_surface, (card_rect.x, card_rect.y + card_rect.height - mask_height))
                        
    def render(self):
        """整合所有繪製方法以更新單一畫格的畫面。繪製順序對於圖層很重要。"""
        self.draw_background()
        self.draw_grid()
        
        # 遊戲世界元素
        self.draw_plants()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_suns()

        # UI 元素在最上層
        self.draw_ui()
        self.draw_cooldowns()

        # 除錯資訊範例 (可選)
        # if hasattr(self.game, 'debug_mode') and self.game.debug_mode and hasattr(self.game, 'clock'):
        #     fps_text = self.font_debug.render(f"FPS: {int(self.game.clock.get_fps())}", True, (255,255,255))
        #     self.screen.blit(fps_text, (10, self.screen_height - 30))
        
        # 繪製自訂滑鼠指標 (如果有的話)
        if self.custom_cursor_surface and not self.default_cursor_visible:
            cursor_pos = pygame.mouse.get_pos()
            # 讓圖示的中心點在滑鼠位置
            self.screen.blit(self.custom_cursor_surface, self.custom_cursor_surface.get_rect(center=cursor_pos))

        # 此處不執行 pygame.display.flip()；這通常在 GameView.render() 被呼叫後於主遊戲迴圈中完成。

    def set_custom_cursor(self, surface):
        """設定自訂滑鼠指標圖像。如果 surface 為 None，則恢復預設指標。"""
        if surface:
            self.custom_cursor_surface = surface
            if self.default_cursor_visible:
                pygame.mouse.set_visible(False)
                self.default_cursor_visible = False
        else:
            self.custom_cursor_surface = None
            if not self.default_cursor_visible:
                pygame.mouse.set_visible(True)
                self.default_cursor_visible = True