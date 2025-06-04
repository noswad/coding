import pygame
from settings import WHITE, YELLOW, UI_SCORE_POS_RATIO, UI_LIVES_OFFSET_X_RATIO, UI_ROUND_POS_Y_OFFSET_RATIO, WIDTH, HEIGHT

def draw_score(screen, font, score):
    """在畫面左上角顯示分數。"""
    score_pos_x = int(WIDTH * UI_SCORE_POS_RATIO[0])
    score_pos_y = int(HEIGHT * UI_SCORE_POS_RATIO[1])
    score_surf = font.render(f"分數: {score}", True, WHITE)
    screen.blit(score_surf, (score_pos_x, score_pos_y))

def draw_lives(screen, font, lives):
    """在畫面右上角顯示生命數。"""
    lives_offset_x = int(WIDTH * UI_LIVES_OFFSET_X_RATIO)
    lives_pos_y = int(HEIGHT * UI_SCORE_POS_RATIO[1])
    lives_surf = font.render(f"生命: {lives}", True, WHITE)
    screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - lives_offset_x, lives_pos_y))

def draw_round(screen, font, round_number):
    """在畫面左上角（分數下方）顯示回合數。"""
    round_pos_x = int(WIDTH * UI_SCORE_POS_RATIO[0])
    round_pos_y = int(HEIGHT * (UI_SCORE_POS_RATIO[1] + UI_ROUND_POS_Y_OFFSET_RATIO))
    round_surf = font.render(f"回合: {round_number}", True, YELLOW)
    screen.blit(round_surf, (round_pos_x, round_pos_y))
    