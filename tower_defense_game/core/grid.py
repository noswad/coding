import pygame
from config import CELL_WIDTH, CELL_HEIGHT, GRID_ROWS, GRID_COLS
from entities.unit import Plant


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(
            col * CELL_WIDTH,
            row * CELL_HEIGHT,
            CELL_WIDTH,
            CELL_HEIGHT
        )
        self.unit = None  # 放置的單位（Plant），預設為 None

    def can_place(self) -> bool:
        return self.unit is None

    def set_unit(self, unit_instance):
        """
        設定此格子的單位。
        假設 can_place() 已在外部檢查過。
        """
        self.unit = unit_instance
    def draw(self, screen, highlight=False):
        # 只畫格線和高亮，不畫單位
        color = (200, 200, 200)
        if highlight:
            color = ((180, 255, 180) if self.can_place()
                     else (255, 180, 180))
        pygame.draw.rect(screen, color, self.rect, 2)


class Grid:
    def __init__(self):
        self.rows = GRID_ROWS
        self.cols = GRID_COLS
        self.cells = [
            [Cell(row, col) for col in range(self.cols)]
            for row in range(self.rows)
        ]
        self.selected_cell = None  # 滑鼠目前指向的格子

    def draw(self, screen):
        """繪製整個網格（所有格子）。
        GameView 可以選擇呼叫此方法來繪製帶有高亮的網格。"""
        mouse_pos = pygame.mouse.get_pos()
        for row in self.cells:
            for cell in row:
                highlight = cell.rect.collidepoint(mouse_pos)
                cell.draw(screen, highlight=highlight)

    # 注意：get_cell 的 x, y 參數是相對於螢幕左上角的像素座標。
    # CELL_WIDTH 和 CELL_HEIGHT 是格子的像素尺寸。
    # 這意味著 Grid 類別假設網格本身是從螢幕的 (0,0) 開始的。
    # 如果您的遊戲畫面中網格有偏移 (例如 GameView 中的 grid_offset_x, grid_offset_y)，
    # 那麼在呼叫 get_cell 或 place_unit_at_pixel_pos 之前，
    # 需要將滑鼠的螢幕座標轉換為相對於網格左上角的座標。
    # 或者，修改 get_cell 以接受一個 offset 參數。
    # 目前的 Game.handle_event 傳遞的是原始 mouse_pos，
    # 而 GameView 的 grid_offset_x/y 是用於 GameView 自己的繪圖。
    # 為了簡化，我們假設 Grid 處理的是相對於螢幕的座標，
    # 並且 CELL_WIDTH/HEIGHT 是全域的。
    # 如果 GameView 的 grid_offset_x/y 不為0，則需要調整傳遞給 Grid 方法的座標。
    # 讓我們假設 Grid 的 (0,0) cell 對應螢幕的 (grid_offset_x, grid_offset_y)
    # 因此，傳遞給 get_cell 的座標應該是
    # mouse_pos[0] - grid_offset_x, mouse_pos[1] - grid_offset_y

    def get_cell(self, x, y):
        """根據像素座標取得格子(row, col)，若超出範圍回傳 None"""
        col = x // CELL_WIDTH
        row = y // CELL_HEIGHT
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None

    def can_place(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        return self.cells[row][col].can_place()

    def place_unit_at_pixel_pos(self, screen_pixel_pos, unit_class,
                                grid_offset_x=0, grid_offset_y=0, **kwargs):
        """
        在給定的螢幕像素座標嘗試放置一個單位。
        如果成功，回傳創建的單位實例，否則回傳 None。
        **kwargs 會傳遞給 unit_class 的建構子 (例如 hp)
        grid_offset_x, grid_offset_y 是網格在螢幕上的
        左上角偏移量。
        """
        grid_relative_x = screen_pixel_pos[0] - grid_offset_x
        grid_relative_y = screen_pixel_pos[1] - grid_offset_y
        cell_rc = self.get_cell(grid_relative_x, grid_relative_y)
        if cell_rc:
            row, col = cell_rc
            target_cell = self.cells[row][col]

            if target_cell.can_place():
                # 計算此格子在螢幕上的中心點座標
                # target_cell.rect 是相對於網格原點的
                screen_cell_center_x = grid_offset_x + target_cell.rect.centerx
                screen_cell_center_y = grid_offset_y + target_cell.rect.centery
                
                # 使用螢幕座標實例化單位
                # unit_class (例如 Plant) 的建構子需要 'grid_pos' 和 'cell_center_pos'
                # **kwargs 來自 Game.handle_event，包含 'game', 'projectile_image_surface' 等
                new_unit = unit_class(
                    grid_pos=(col, row),  # 邏輯網格位置
                    cell_center_pos=(screen_cell_center_x, screen_cell_center_y),  # 螢幕像素中心點
                    **kwargs 
                )
                target_cell.set_unit(new_unit)  # 在格子中儲存單位
                return new_unit  # 回傳創建的單位
        return None


# 單元測試（可用 pytest 或直接執行）
def _test_grid_place_unit():
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode(  # noqa: F841 (screen is not used directly in test logic but needed for pygame)
        (CELL_WIDTH * GRID_COLS, CELL_HEIGHT * GRID_ROWS)
    )
    grid = Grid()
    # 測試 get_cell
    assert grid.get_cell(10, 10) == (0, 0)
    assert grid.get_cell(CELL_WIDTH * 2 + 1,
                         CELL_HEIGHT * 3 + 1) == (3, 2)
    assert grid.get_cell(-1, -1) is None
    assert grid.get_cell(CELL_WIDTH * GRID_COLS + 1, 0) is None

    # 測試 can_place 與 place_unit_at
    assert grid.can_place(0, 0)
    # place_unit_at_pixel_pos 需要 unit_class，並且 place_unit
    # 會回傳實例，可以傳遞額外參數
    # 為了測試 place_unit_at_pixel_pos，我們需要模擬 grid_offset
    # 並確保 Plant 的 cell_center_pos 是正確的螢幕座標
    # Plant 的建構子需要 grid_pos 和 cell_center_pos
    # Grid.place_unit_at_pixel_pos 現在會處理這些
    placed_unit = grid.place_unit_at_pixel_pos((10,10), Plant, grid_offset_x=0, grid_offset_y=0, hp=100)
    assert placed_unit is not None
    assert placed_unit.rect.center == (grid.cells[0][0].rect.centerx, grid.cells[0][0].rect.centery) # 檢查是否使用螢幕座標
    assert not grid.can_place(0, 0)
    # 已放置不能再放
    assert grid.place_unit_at_pixel_pos((10,10), Plant, grid_offset_x=0, grid_offset_y=0, hp=100) is None


    print("Grid 單元測試通過")

if __name__ == "__main__":
    _test_grid_place_unit()