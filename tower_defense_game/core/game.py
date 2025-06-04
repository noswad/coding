# core/game.py
import pygame
import sys
import os
import random # For enemy spawning

# 將 'tower_defense_game' 目錄 (core 的父目錄) 新增到 sys.path，
# 這樣可以從 'tower_defense_game' 目錄匯入模組，例如 'game_view'。
# __file__ 是 d:\coding\tower_defense_game\core\game.py。
# os.path.dirname(os.path.abspath(__file__)) 是 d:\coding\tower_defense_game\core。
# os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# 是 d:\coding\tower_defense_game。
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
)

from game_view import GameView  # 假設 game_view.py 在父目錄中
from core.grid import Grid  # 匯入 Grid 類別
from entities.sunflower import Sunflower as SunflowerLogic # Renamed for clarity
from entities.enemy import Enemy # Import Enemy
from entities.peashooter import (
    Peashooter as PeashooterLogic,
    SnowPea as SnowPeaLogic,
    Repeater as RepeaterLogic,
    GatlingPea as GatlingPeaLogic,
    SnowPeaImproved as SnowPeaImprovedLogic
)
from entities.animated_peashooter import (
    Peashooter as AnimatedPeashooterVisuals,
    DEFAULT_PLANT_TYPE as ANIMATED_PEASHOOTER_DEFAULT_TYPE # Import the constant
)
from entities.animated_sunflower import AnimatedSunflower
from core.ui_elements import PlantCard # Use the new PlantCard class
from core.resource_manager import ResourceManager # Import ResourceManager


class Game:
    def __init__(self, screen_surface, config_module):
        self.screen = screen_surface
        self.config = config_module  # 儲存設定模組
        self.game_over = False
        self.clock = pygame.time.Clock()  # GameView 可能會透過 self.game.clock 顯示 FPS

        # 初始化遊戲狀態列表
        self.plants = []  # Plant 物件列表
        self.enemies = []  # Enemy 物件列表
        self.projectiles = []  # Projectile 物件列表

        self.player_sun = self.config.INITIAL_RESOURCES

        self.plant_cards = [] # Will be populated by _initialize_assets_and_cards
        self.shovel_selected = False  # 供 GameView 強調鏟子
        self.selected_plant_card = None  # Store the selected PlantCard object

        # 初始化遊戲網格
        self.grid = Grid()

        # Asset loaders for visuals (to get seed packets and projectile images)
        self.peashooter_asset_loader = AnimatedPeashooterVisuals() # Will use set_plant_type
        self.sunflower_asset_loader = AnimatedSunflower()

        # Initialize ResourceManager
        self.resource_manager = ResourceManager(self)

        self._initialize_plant_cards()

        # 初始化 GameView
        self.view = GameView(self.screen, self)  # 將 self (Game 實例) 作為 game_logic 傳遞

        # 確保 GameView 中的 card_rects 在 GameView 初始化後立即計算，
        # 因為 handle_event 可能會在其第一次被呼叫時就存取它們。
        # 如果 _calculate_card_rects 依賴於 self.game.plant_cards，
        # 則 GameView 的 __init__ 中的順序應該是正確的。
        # 如果 GameView 的 __init__ 中 _calculate_card_rects 尚未執行
        # 或 plant_cards 為空，則 self.view.card_rects 可能為空列表。
        # 這裡假設 GameView.__init__ 會正確處理。
        
        # Enemy spawning attributes
        self.enemy_spawn_timer = pygame.time.get_ticks() # Initialize with current time
        self.enemy_spawn_interval = 5000  # Spawn enemy every 5 seconds (milliseconds)

    def _initialize_plant_cards(self):
        """Initializes the list of PlantCard objects for the game."""
        # Define Plant Costs and Cooldowns (could be in config.py or here)
        # Using config.PLANT_COOLDOWN as a base, specific plants might have multipliers
        base_cooldown = self.config.PLANT_COOLDOWN

        plant_data_definitions = [
            # 第一張固定為太陽花
            {"name": "Sunflower", "logic_class": SunflowerLogic, "cost": 50,
             "cooldown_ms": base_cooldown, "asset_loader_type": "sunflower",
             "unit_kwargs": {"game": self}},
            # 其他植物卡片
            {"name": "Peashooter", "logic_class": PeashooterLogic, "cost": 100,
             "cooldown_ms": base_cooldown, "asset_loader_type": "peashooter",
             "projectile_image_key": "pea", "unit_kwargs": {"game": self}},
            {"name": "SnowPea", "logic_class": SnowPeaLogic, "cost": 175,
             "cooldown_ms": base_cooldown, "asset_loader_type": "peashooter",
             "projectile_image_key": "pea", "unit_kwargs": {"game": self}},
            # 確保總共有6張卡片，您可以根據需要調整或新增以下卡片
            {"name": "RepeaterPea", "logic_class": RepeaterLogic, "cost": 200,
             "cooldown_ms": int(base_cooldown * 1.2), "asset_loader_type": "peashooter",
             "visual_type_for_assets": "Peashooter", # Repeater uses Peashooter's pea
             "projectile_image_key": "pea", "unit_kwargs": {"game": self}},
            {"name": "SnowPeaImproved", "logic_class": SnowPeaImprovedLogic, "cost": 225,
             "cooldown_ms": int(base_cooldown * 1.5), "asset_loader_type": "peashooter",
             "visual_type_for_assets": "SnowPea", # Uses SnowPea's assets
             "projectile_image_key": "improved_pea", "unit_kwargs": {"game": self}},
            {"name": "GatlingPea", "logic_class": GatlingPeaLogic, "cost": 250,
             "cooldown_ms": int(base_cooldown * 1.8), "asset_loader_type": "peashooter",
             "projectile_image_key": "fire_pea", "unit_kwargs": {"game": self}},
            # 如果需要更多卡片，可以在此處新增，例如堅果牆 (WallNut)
            # 您需要先定義 WallNutLogic 和相關的視覺資源 (如果它有動畫或特殊種子包)
            # {
            #     "name": "WallNut", 
            #     "logic_class": WallNutLogic, # 假設您已創建 WallNutLogic
            #     "cost": 50,
            #     "cooldown_ms": int(base_cooldown * 2.0), 
            #     "asset_loader_type": "peashooter", # 或者為堅果創建一個新的 asset_loader
            #     "visual_type_for_assets": "WallNut", # 假設 WallNut 是 PLANT_DATA_CONFIG 中的一個類型
            #     "unit_kwargs": {"game": self}
            # },
        ]

        for data in plant_data_definitions:
            icon_surface = None
            projectile_img_surface = None
            cursor_image_surface = None
            
            # Determine which asset loader and visual type to use
            visual_type = data.get("visual_type_for_assets", data["name"])

            if data["asset_loader_type"] == "sunflower":
                icon_surface = self.sunflower_asset_loader.seed_packet_image
                # Sunflowers don't shoot, so no projectile_image_key needed
                # Get cursor image (first frame of "idle" animation)
                idle_anim_data = self.sunflower_asset_loader.animations.get("idle")
                if idle_anim_data and idle_anim_data["frames"]:
                    cursor_image_surface = idle_anim_data["frames"][0]
            elif data["asset_loader_type"] == "peashooter":
                self.peashooter_asset_loader.set_plant_type(visual_type)
                icon_surface = self.peashooter_asset_loader.get_static_image("seed_packet")
                idle_anim_data_pea = self.peashooter_asset_loader.animations_for_current_type.get("Idle") # "Idle" is default action
                if idle_anim_data_pea and idle_anim_data_pea["frames"]:
                    cursor_image_surface = idle_anim_data_pea["frames"][0]
                if data.get("projectile_image_key"): # Use .get for safety
                    projectile_img_surface = self.peashooter_asset_loader.get_static_image(data["projectile_image_key"])
                    if projectile_img_surface:
                         data["unit_kwargs"]["projectile_image_surface"] = projectile_img_surface
                    else:
                        print(f"Warning: Could not load projectile image '{data['projectile_image_key']}' for {data['name']}")

            if icon_surface:
                self.plant_cards.append(PlantCard(
                    plant_name=data["name"],
                    cost=data["cost"],
                    cooldown_ms=data["cooldown_ms"],
                    icon_surface=icon_surface,
                    plant_class_to_spawn=data["logic_class"],
                    cursor_image=cursor_image_surface, # Pass the cursor image
                    asset_loader_type=data["asset_loader_type"],
                    visual_type_for_assets=visual_type
                ))
                # Store unit_kwargs directly in the card for later use when spawning
                self.plant_cards[-1].unit_kwargs = data.get("unit_kwargs", {})
            else:
                print(f"Warning: Could not load seed packet icon for {data['name']}")
        
        # Reset peashooter_asset_loader to default if it was used
        if any(d["asset_loader_type"] == "peashooter" for d in plant_data_definitions):
            self.peashooter_asset_loader.set_plant_type(ANIMATED_PEASHOOTER_DEFAULT_TYPE)

    def trigger_game_over(self):
        """Sets the game over flag."""
        if not self.game_over: # 避免重複觸發
            self.game_over = True
            print("Game Over triggered!") # 可以在此處新增更多遊戲結束邏輯

    def update(self):
        if self.game_over:
            return

        current_time_seconds = pygame.time.get_ticks() / 1000.0
        current_ticks_ms = pygame.time.get_ticks()

        # --- 範例遊戲邏輯 ---
        # 更新植物、敵人、投射物、陽光
        # 注意：變數名稱改為 plant_instance 以避免與 Plant 類別混淆
        print(f"[DEBUG GAME UPDATE] Plants list before update loop: {[(p.name, id(p), p.hp) for p in self.plants]}") # DEBUG: Show plants in list
        for plant_instance in self.plants:
            # Sunflower has a different update signature, other plants expect enemies
            if isinstance(plant_instance, SunflowerLogic):
                plant_instance.update() 
            else:
                plant_instance.update(self.enemies)

            # Detailed check for visual_component update
            print(f"[DEBUG GAME UPDATE] Checking visual_component for {plant_instance.name} ID: {id(plant_instance)}")
            if hasattr(plant_instance, 'visual_component'):
                print(f"[DEBUG GAME UPDATE] -> {plant_instance.name} ID: {id(plant_instance)} HAS visual_component attribute.")
                if plant_instance.visual_component:
                    print(f"[DEBUG GAME UPDATE] -> {plant_instance.name} ID: {id(plant_instance)} visual_component IS NOT None. Type: {type(plant_instance.visual_component)}. Calling update...")
                    plant_instance.visual_component.update() # This should call AnimatedSunflower.update()
                else:
                    print(f"[DEBUG GAME UPDATE] -> {plant_instance.name} ID: {id(plant_instance)} visual_component IS None. Update SKIPPED.")
            else:
                print(f"[DEBUG GAME UPDATE] -> {plant_instance.name} ID: {id(plant_instance)} DOES NOT HAVE visual_component attribute. Update SKIPPED.")

 
        # 更新敵人
        for enemy_instance in self.enemies:
            enemy_instance.update(self.plants, current_time_seconds, self.trigger_game_over)

        # 更新投射物
        for projectile_instance in self.projectiles:
            projectile_instance.update(self.enemies) # 傳遞敵人列表以供碰撞檢測

        # 清理死去的單位和投射物
        # 確保 sprite 的 alive() 方法被檢查 (如果它們是 Sprite 的子類別)
        self.plants = [p for p in self.plants if p.hp > 0]
        self.enemies = [e for e in self.enemies if e.hp > 0 and e.alive()]
        self.projectiles = [p for p in self.projectiles if not p.is_dead] # Projectile.is_dead 用於判斷

        if current_ticks_ms - self.enemy_spawn_timer > self.enemy_spawn_interval:
            random_row = random.randint(0, self.config.GRID_ROWS - 1)
            spawn_y_center = self.view.grid_offset_y + (random_row * self.config.CELL_HEIGHT) + (self.config.CELL_HEIGHT // 2)
            new_enemy = Enemy(pos=(self.screen.get_width(), spawn_y_center))
            self.enemies.append(new_enemy)
            self.enemy_spawn_timer = current_ticks_ms
        
        # Update suns via ResourceManager
        self.resource_manager.update()

    def draw(self):
        """將所有繪圖委派給 GameView。"""
        self.view.render()

    def handle_event(self, event):
        """處理遊戲特定事件。"""
        if self.game_over:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左鍵點擊
            mouse_pos = event.pos

            # 如果處於放置模式，先處理放置或取消
            if self.selected_plant_card and not self.shovel_selected:
                # 點擊網格放置植物的邏輯已在下方處理
                pass # 讓後續的網格點擊邏輯處理
            elif self.shovel_selected:
                # 點擊網格移除植物的邏輯已在下方處理
                pass

            # --- UI 元素點擊檢查 ---

            # 檢查鏟子點擊
            if self.view.shovel_button_rect.collidepoint(mouse_pos):
                self.shovel_selected = not self.shovel_selected
                self.selected_plant_card = None  # 如果選中鏟子，取消選中植物
                print(f"鏟子選取狀態：{self.shovel_selected}")
                return

            # 檢查卡片點擊 (範例)
            # 確保 self.view.card_rects 在此時已由 GameView 初始化
            card_rects_to_check = (self.view.card_rects
                                   if hasattr(self.view, 'card_rects') else [])
            for i, card_rect in enumerate(card_rects_to_check):
                if card_rect.collidepoint(mouse_pos):
                    card = self.plant_cards[i]
                    if card.can_be_selected(self.player_sun):
                        if self.selected_plant_card: # Deselect previous card
                            self.selected_plant_card.is_selected = False
                        
                        self.selected_plant_card = card  # 選取此卡片以供放置
                        self.selected_plant_card.is_selected = True
                        self.shovel_selected = False  # 取消選中鏟子
                        # 設定自訂滑鼠指標
                        if self.selected_plant_card.cursor_image:
                            self.view.set_custom_cursor(self.selected_plant_card.cursor_image)
                        else: # Fallback if cursor image isn't loaded
                            self.view.set_custom_cursor(self.selected_plant_card.icon_surface) # Use card icon as fallback
                        print(
                            f"卡片 '{self.selected_plant_card.plant_name}' 已選取待放置 "
                            f"(花費：{card.cost})。"
                        )
                    elif card.get_cooldown_progress() > 0.0:
                        print(f"卡片 '{card.plant_name}' 正在冷卻中。") # 使用 card.plant_name
                    elif self.player_sun < card.cost:
                        print(
                            f"陽光不足以購買 '{card.plant_name}'。"
                            f"需要 {card.cost}，目前擁有 {self.player_sun}。"
                        )
                    return

            # 檢查網格點擊以放置植物或使用鏟子
            if self.selected_plant_card and not self.shovel_selected:
                # 這裡我們假設 place_unit_at_pixel_pos 接收的是相對於螢幕的
                # mouse_pos，並且它內部會正確處理到網格的轉換。
                # 根據 core/grid.py 的 get_cell，它期望的是相對於螢幕的座標。
                new_plant = self.grid.place_unit_at_pixel_pos(
                    mouse_pos,
                    self.selected_plant_card.plant_class_to_spawn,
                    grid_offset_x=self.view.grid_offset_x, # Pass grid offset
                    grid_offset_y=self.view.grid_offset_y, # Pass grid offset
                    **self.selected_plant_card.unit_kwargs # Use stored kwargs
                )
                if new_plant:
                    print(f"[DEBUG GAME] New plant created: {new_plant.name} with ID: {id(new_plant)} at {new_plant.grid_pos}, rect: {new_plant.rect}") # DEBUG
                    self.plants.append(new_plant)
                    self.player_sun -= self.selected_plant_card.cost
                    
                    # 創建並附加動畫視覺組件
                    card_ref = self.selected_plant_card # 為了清晰
                    visual_component = None
                    if card_ref.asset_loader_type == "sunflower":
                        visual_component = AnimatedSunflower(position=new_plant.rect.center)
                    elif card_ref.asset_loader_type == "peashooter":
                        print(f"[DEBUG] Creating AnimatedPeashooterVisuals with type: '{card_ref.visual_type_for_assets}', position: {new_plant.rect.center}") # DEBUG
                        visual_component = AnimatedPeashooterVisuals(
                            plant_type=card_ref.visual_type_for_assets, 
                            position=new_plant.rect.center
                        )
                        # AnimatedPeashooterVisuals 預設為 Idle 狀態

                    if visual_component:
                        new_plant.visual_component = visual_component
                    
                    self.selected_plant_card.start_cooldown() # Use PlantCard's method
                    self.selected_plant_card.is_selected = False # 取消選中
                    self.selected_plant_card = None # Deselect after placing
                    self.view.set_custom_cursor(None) # 恢復預設滑鼠指標
                else:
                    # 檢查點擊是否在網格內但格子不可放置
                    grid_relative_x = mouse_pos[0] - self.view.grid_offset_x
                    grid_relative_y = mouse_pos[1] - self.view.grid_offset_y
                    cell_rc = self.grid.get_cell(grid_relative_x, grid_relative_y)
                    if cell_rc:
                        row, col = cell_rc
                        if not self.grid.cells[row][col].can_place():
                             print(f"無法放置：格子 ({row},{col}) 已被佔用或無效。")
                        # else: # 這種情況不應該發生，如果 get_cell 有效但 place_unit_at_pixel_pos 失敗
                    else:
                        print("點擊位置在網格之外，無法放置植物。")
                        # 如果點擊網格外，也應該取消放置模式
                        if self.selected_plant_card:
                            self.selected_plant_card.is_selected = False
                            self.selected_plant_card = None
                            self.view.set_custom_cursor(None)

            elif self.shovel_selected:
                # 在此處新增用鏟子移除植物的邏輯
                print(f"嘗試在滑鼠位置 {mouse_pos} 使用鏟子。")
                self.shovel_selected = False  # 使用一次後取消選中鏟子
                self.view.set_custom_cursor(None) # 恢復預設滑鼠指標 (如果鏟子也改變了指標)
            else:
                # If no UI element was clicked, and not placing/shoveling, check for sun collection
                # This 'else' assumes that if a card was selected or shovel was selected,
                # the click was either on the grid (handled above) or outside (and placement cancelled).
                # We need to ensure this doesn't conflict with clicking empty grid space when nothing is selected.
                
                # A more robust way to check if the click was NOT on a UI element:
                clicked_on_ui_card_or_shovel_button = False
                if self.view.shovel_button_rect.collidepoint(mouse_pos):
                    clicked_on_ui_card_or_shovel_button = True
                if not clicked_on_ui_card_or_shovel_button:
                    for card_rect_check in self.view.card_rects:
                        if card_rect_check.collidepoint(mouse_pos):
                            clicked_on_ui_card_or_shovel_button = True
                            break
                
                if not clicked_on_ui_card_or_shovel_button: # If click was not on a card or shovel button
                    collected_value = self.resource_manager.handle_click(mouse_pos)
                    if collected_value > 0:
                        self.player_sun += collected_value
                        print(f"收集到 {collected_value} 陽光。總計：{self.player_sun}")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # 右鍵點擊
            if self.selected_plant_card: # 如果正在放置植物
                print("取消放置植物。")
                self.selected_plant_card.is_selected = False
                self.selected_plant_card = None
                self.view.set_custom_cursor(None) # 恢復預設滑鼠指標

        # 可在此處處理其他事件，如鍵盤輸入等
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.selected_plant_card: # 如果正在放置植物
                    print("取消放置植物 (ESC)。")
                    self.selected_plant_card.is_selected = False
                    self.selected_plant_card = None
                    self.view.set_custom_cursor(None) # 恢復預設滑鼠指標
                elif self.shovel_selected: # 如果選中了鏟子
                    print("取消選取鏟子 (ESC)。")
                    self.shovel_selected = False
                    self.view.set_custom_cursor(None)