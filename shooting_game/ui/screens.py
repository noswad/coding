import pygame
from settings import WHITE, YELLOW, RED, WIDTH, HEIGHT

def draw_start_screen(screen, title_font, chinese_font, small_font, high_score):
    """繪製開始畫面。"""
    title_y_ratio = 1/3
    prompt_y_ratio = 1/2
    hs_y_offset_ratio = 0.1  # 60/600 from prompt

    title_surf = title_font.render("太空貓咪大戰外星生物", True, WHITE)
    prompt_surf = chinese_font.render("按 SPACE 開始遊戲", True, WHITE)
    hs_surf = small_font.render(f"最高分數: {high_score}", True, YELLOW)
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, int(HEIGHT * title_y_ratio)))
    screen.blit(prompt_surf, (WIDTH // 2 - prompt_surf.get_width() // 2, int(HEIGHT * prompt_y_ratio)))
    screen.blit(hs_surf, (WIDTH // 2 - hs_surf.get_width() // 2, int(HEIGHT * prompt_y_ratio + HEIGHT * hs_y_offset_ratio)))

def draw_game_over_screen(screen, title_font, chinese_font, score, high_score):
    """繪製遊戲結束畫面。"""
    game_over_y_ratio = 1/4
    final_score_y_offset_ratio = -0.05  # -30/600 from center
    high_score_y_offset_ratio = 0.0333  # 20/600 from center
    restart_y_offset_ratio = 0.1166     # 70/600 from center

    game_over_surf = title_font.render("遊戲結束", True, RED)
    final_score_surf = chinese_font.render(f"你的分數: {score}", True, WHITE)
    high_score_surf = chinese_font.render(f"最高分數: {high_score}", True, YELLOW)
    restart_surf = chinese_font.render("按 R 重新開始", True, WHITE)
    screen.blit(game_over_surf, (WIDTH // 2 - game_over_surf.get_width() // 2, int(HEIGHT * game_over_y_ratio)))
    screen.blit(final_score_surf, (WIDTH // 2 - final_score_surf.get_width() // 2, int(HEIGHT // 2 + HEIGHT * final_score_y_offset_ratio)))
    screen.blit(high_score_surf, (WIDTH // 2 - high_score_surf.get_width() // 2, int(HEIGHT // 2 + HEIGHT * high_score_y_offset_ratio)))
    screen.blit(restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, int(HEIGHT // 2 + HEIGHT * restart_y_offset_ratio)))