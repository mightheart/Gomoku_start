"""
工具函数文件
"""
import pygame
import os
from utils.constants import *
import time
from functools import wraps

pygame.font.init()

# 获取 frontend_2d 目录的绝对路径
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend_2d")

def load_background_image():
    """加载背景图片"""
    try:
        background_path = os.path.join(FRONTEND_DIR, "data", "background1.jpg")
        background_image = pygame.image.load(background_path)
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return background_image
    except Exception as e:
        print(f"背景图片加载失败: {e}")
        return None

def load_fonts():
    """加载字体"""
    try:
        font_path = os.path.join(FRONTEND_DIR, 'font', '12345.TTF')
        font_large = pygame.font.Font(font_path, 48)
        font_medium = pygame.font.Font(font_path, 36)
        font_small = pygame.font.Font(font_path, 24)
    except Exception as e:
        print(f"自定义字体加载失败，使用系统字体: {e}")
        font_large = pygame.font.SysFont("simhei", 48)
        font_medium = pygame.font.SysFont("simhei", 36)
        font_small = pygame.font.SysFont("simhei", 24)
    return font_large, font_medium, font_small

def get_board_position_from_mouse(mouse_pos, board_x, board_y, board_size):
    x, y = mouse_pos
    board_width = board_size * CELL_SIZE
    board_height = board_size * CELL_SIZE
    if (board_x <= x <= board_x + board_width and
        board_y <= y <= board_y + board_height):
        col = (x - board_x) // CELL_SIZE
        row = (y - board_y) // CELL_SIZE
        if 0 <= row < board_size and 0 <= col < board_size:
            return row, col
    return None, None

def timer(func):
    """监测函数运行时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"函数 {func.__name__} 执行时间: {execution_time:.4f} 秒")
        return result
    return wrapper

