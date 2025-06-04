# main.py
import pygame
from core.game import Game
import config as game_config # 匯入遊戲設定

# Constants for main.py
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BUTTON_GREEN = (0, 150, 0)
COLOR_BUTTON_HOVER_GREEN = (0, 200, 0)

# Fonts
DEFAULT_FONT_NAME = "Arial"
GAME_OVER_FONT_SIZE = 72
RESTART_BUTTON_FONT_SIZE = 40

# Text
GAME_TITLE = "塔防遊戲 - 植物大戰殭屍風格"
GAME_OVER_MESSAGE = "GAME OVER"
RESTART_BUTTON_LABEL = "Restart"

# UI Layout
RESTART_BUTTON_Y_OFFSET_FROM_CENTER = 100
GAME_OVER_TEXT_Y_OFFSET_FROM_CENTER = -50
RESTART_BUTTON_PADDING_X = 20
RESTART_BUTTON_PADDING_Y = 10
RESTART_BUTTON_BORDER_RADIUS = 10


def initialize_game(screen_surface):
    """Initializes or re-initializes the game state."""
    return Game(screen_surface, game_config) # 傳遞設定模組


def draw_game_over_screen(screen, game_over_font, restart_button_text_surface, restart_button_rect):
    """
    繪製遊戲結束畫面，包含 "GAME OVER" 訊息和重新開始按鈕。

    Args:
        screen: Pygame 的螢幕表面。
        game_over_font: 用於 "GAME OVER" 訊息的字型。
        restart_button_text_surface: 已渲染的重新開始按鈕文字表面。
        restart_button_rect: 重新開始按鈕文字的矩形區域，用於定位。
    """
    screen.fill(COLOR_BLACK)  # 黑色背景

    # 繪製 "GAME OVER" 訊息
    game_over_text_surface = game_over_font.render(GAME_OVER_MESSAGE, True, COLOR_RED)
    game_over_text_rect = game_over_text_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + GAME_OVER_TEXT_Y_OFFSET_FROM_CENTER)
    )
    screen.blit(game_over_text_surface, game_over_text_rect)

    # 繪製重新開始按鈕
    mouse_pos = pygame.mouse.get_pos()
    is_hovering_restart = restart_button_rect.collidepoint(mouse_pos)
    current_button_color = COLOR_BUTTON_HOVER_GREEN if is_hovering_restart else COLOR_BUTTON_GREEN
    drawn_button_rect = restart_button_rect.inflate(RESTART_BUTTON_PADDING_X, RESTART_BUTTON_PADDING_Y)
    pygame.draw.rect(screen, current_button_color, drawn_button_rect, border_radius=RESTART_BUTTON_BORDER_RADIUS)
    screen.blit(restart_button_text_surface, restart_button_rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    game = initialize_game(screen)

    # 遊戲結束畫面的字型和重新開始按鈕的資源
    restart_font = pygame.font.SysFont(DEFAULT_FONT_NAME, RESTART_BUTTON_FONT_SIZE)
    game_over_font = pygame.font.SysFont(DEFAULT_FONT_NAME, GAME_OVER_FONT_SIZE)
    restart_button_text = restart_font.render(RESTART_BUTTON_LABEL, True, COLOR_WHITE)
    restart_button_rect = restart_button_text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_BUTTON_Y_OFFSET_FROM_CENTER)
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button_rect.collidepoint(event.pos):
                        game = initialize_game(screen)
                        continue # 明確跳過此事件的後續處理
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Allow restarting with 'R' key
                        game = initialize_game(screen)
                        continue # 明確跳過此事件的後續處理
            else:
                game.handle_event(event)

        if not game.game_over: # 只有在遊戲未結束時才更新和繪製
            game.update()
            game.draw()
        else:
            draw_game_over_screen(screen, game_over_font, restart_button_text, restart_button_rect)
            
        pygame.display.flip() # 每次循環都應該更新顯示
        clock.tick(FPS) # 控制幀率

    pygame.quit()


if __name__ == "__main__":
    main()