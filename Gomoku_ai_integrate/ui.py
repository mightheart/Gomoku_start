"""
界面绘制相关功能
"""
import pygame
from constants import *
from utils import load_background_image, load_fonts

class GameUI:
    """游戏界面类"""
    
    def __init__(self):
        self.background_image = load_background_image()
        self.font_large, self.font_medium, self.font_small = load_fonts()
        self.board_x = (SCREEN_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
        self.board_y = 120
    
    def draw_background(self, screen):
        """绘制背景"""
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(LIGHT_BROWN)
    
    def draw_menu(self, screen):
        """绘制开始菜单"""
        self.draw_background(screen)
        
        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        screen.blit(overlay, (0, 0))
        
        # 标题
        title_text = self.font_large.render("五子棋人机对战", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # 游戏说明
        rules = [
            "游戏规则：",
            "1. 玩家与AI轮流下棋",
            "2. 先连成5子者获胜",
            "3. 可横、竖、斜连线",
            "",
            "按键说明：",
            "U键: 撤回",
            "D键: 恢复", 
            "R键: 重新开始",
            "M键: 返回菜单",
            "",
            "点击任意位置开始游戏"
        ]
        
        y_offset = 200
        for rule in rules:
            rule_text = self.font_small.render(rule, True, BLACK)
            rule_rect = rule_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(rule_text, rule_rect)
            y_offset += 30
    
    def draw_side_selection(self, screen):
        """绘制执棋方选择界面"""
        self.draw_background(screen)
        
        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        screen.blit(overlay, (0, 0))
        
        # 标题
        title_text = self.font_medium.render("选择执棋方", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # 按钮
        button1_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 60)
        button2_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 370, 300, 60)
        
        pygame.draw.rect(screen, WHITE, button1_rect)
        pygame.draw.rect(screen, BLACK, button1_rect, 2)
        pygame.draw.rect(screen, WHITE, button2_rect)
        pygame.draw.rect(screen, BLACK, button2_rect, 2)
        
        text1 = self.font_medium.render("执黑先行", True, BLACK)
        text2 = self.font_medium.render("执白后行", True, BLACK)
        
        text1_rect = text1.get_rect(center=button1_rect.center)
        text2_rect = text2.get_rect(center=button2_rect.center)
        
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
        
        return button1_rect, button2_rect
    
    def draw_board(self, screen):
        """绘制棋盘"""
        # 绘制棋盘背景
        board_rect = pygame.Rect(self.board_x - 20, self.board_y - 20,
                                BOARD_SIZE * CELL_SIZE + 40, BOARD_SIZE * CELL_SIZE + 40)
        pygame.draw.rect(screen, BROWN, board_rect)
        
        # 绘制网格线
        for i in range(BOARD_SIZE):
            # 垂直线
            start_x = self.board_x + CELL_SIZE // 2
            end_x = self.board_x + CELL_SIZE // 2
            start_y = self.board_y + CELL_SIZE // 2
            end_y = self.board_y + (BOARD_SIZE - 1) * CELL_SIZE + CELL_SIZE // 2
            
            line_x = start_x + i * CELL_SIZE
            pygame.draw.line(screen, BLACK, (line_x, start_y), (line_x, end_y), 2)
            
            # 水平线
            start_x = self.board_x + CELL_SIZE // 2
            end_x = self.board_x + (BOARD_SIZE - 1) * CELL_SIZE + CELL_SIZE // 2
            line_y = start_y + i * CELL_SIZE
            pygame.draw.line(screen, BLACK, (start_x, line_y), (end_x, line_y), 2)
        
        # 绘制天元
        center = BOARD_SIZE // 2
        x = self.board_x + center * CELL_SIZE + CELL_SIZE // 2
        y = self.board_y + center * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, BLACK, (x, y), 4)
    
    def draw_pieces(self, screen, board, winning_five=None):
        """绘制棋子"""
        if winning_five is None:
            winning_five = []
            
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] != PIECE_EMPTY:
                    x = self.board_x + col * CELL_SIZE + CELL_SIZE // 2
                    y = self.board_y + row * CELL_SIZE + CELL_SIZE // 2
                    
                    # 判断棋子颜色
                    piece_color = BLACK if board[row][col] == PIECE_BLACK else WHITE
                    
                    # 如果是获胜的五子，添加金色边框
                    if (row, col) in winning_five:
                        pygame.draw.circle(screen, GOLD, (x, y), 18, 4)
                    
                    # 绘制棋子
                    pygame.draw.circle(screen, piece_color, (x, y), 15)
                    pygame.draw.circle(screen, BLACK, (x, y), 15, 2)
    
    def draw_game_info(self, screen, current_player, winner, move_history, undo_stack, ai_thinking, player_side):
        """绘制游戏信息"""
        # 当前玩家提示
        if winner == 0:
            if current_player == PLAYER_BLACK:
                player_text = self.font_medium.render("当前: 黑方", True, BLACK)
            else:
                player_text = self.font_medium.render("当前: 白方", True, BLACK)
        else:
            if winner == PLAYER_BLACK:
                player_text = self.font_medium.render("黑方获胜！", True, RED)
            else:
                player_text = self.font_medium.render("白方获胜！", True, RED)
        
        screen.blit(player_text, (50, 10))
        
        # 按键提示
        restart_text = self.font_small.render("R键: 重新开始", True, GRAY)
        menu_text = self.font_small.render("M键/ESC: 返回菜单", True, GRAY)
        
        # 根据状态显示撤回/恢复提示
        if len(move_history) > 0 and not ai_thinking:
            undo_text = self.font_small.render(f"U键: 撤回 ({len(move_history)}步)", True, GRAY)
        else:
            undo_text = self.font_small.render("U键: 撤回 (不可用)", True, (160, 160, 160))
            
        if len(undo_stack) > 0 and not ai_thinking:
            redo_text = self.font_small.render(f"D键: 恢复 ({len(undo_stack)}步)", True, GRAY)
        else:
            redo_text = self.font_small.render("D键: 恢复 (不可用)", True, (160, 160, 160))
        
        screen.blit(restart_text, (SCREEN_WIDTH - 220, 10))
        screen.blit(menu_text, (SCREEN_WIDTH - 220, 40))
        screen.blit(undo_text, (SCREEN_WIDTH - 220, 70))
        screen.blit(redo_text, (SCREEN_WIDTH - 220, 100))
        
        # 显示思考状态
        if ai_thinking and winner == 0 and current_player != player_side:
            thinking_text = self.font_small.render("AI思考中...", True, RED)
            screen.blit(thinking_text, (50, 50))