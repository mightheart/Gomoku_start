"""
常量定义文件
"""
import pygame

# 初始化 Pygame
pygame.init()

# 设置常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 40


# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)  # 用于高亮获胜棋子

# 游戏状态
GAME_STATE_MENU = "menu"
GAME_STATE_SELECT_SIZE = "select_size"  # 新增
GAME_STATE_SELECT_SIDE = "select_side"
GAME_STATE_PLAYING = "playing"

# 玩家标识
PLAYER_BLACK = 1
PLAYER_WHITE = 2

# 棋子符号
PIECE_BLACK = 'X'
PIECE_WHITE = 'O'
PIECE_EMPTY = ' '