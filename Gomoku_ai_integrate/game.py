"""
游戏主类
"""
import pygame
import sys
from constants import *
from ui import GameUI
from ai import AIPlayer
from utils import check_winner_at_position, find_winning_line, get_board_position_from_mouse

class GobangGame:
    """五子棋游戏主类"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("五子棋人机对战")
        self.clock = pygame.time.Clock()
        
        # 初始化组件
        self.ui = GameUI()
        self.ai_player = AIPlayer()
        
        # 游戏状态
        self.game_state = GAME_STATE_MENU
        self.board_size = 15  # 默认15
        self.board = []
        self.current_player = PLAYER_BLACK
        self.winner = 0
        self.winning_five = []
        self.player_side = PLAYER_BLACK
        
        # 用于撤回/恢复功能
        self.move_history = []
        self.undo_stack = []
        
        # 键盘状态跟踪
        self.last_key_time = {}
        
        # 初始化棋盘
        self.reset_game()
    
    def reset_game(self):
        """重置游戏"""
        print("游戏重置")
        self.board = [[PIECE_EMPTY for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = PLAYER_BLACK
        self.winner = 0
        self.winning_five = []
        self.move_history = []
        self.undo_stack = []
        self.ai_player.thinking = False
    
    def place_piece(self, row, col):
        """放置棋子"""
        if self.board[row][col] == PIECE_EMPTY and self.winner == 0:
            # 根据当前玩家确定棋子类型
            piece = PIECE_BLACK if self.current_player == PLAYER_BLACK else PIECE_WHITE
            self.board[row][col] = piece
            
            # 记录落子历史
            self.move_history.append((row, col, self.current_player))
            
            # 清空恢复栈
            self.undo_stack = []
            
            print(f"玩家{self.current_player}在({row},{col})落子")
            
            # 检查是否获胜
            if check_winner_at_position(self.board, row, col, self.board_size):
                self.winner = self.current_player
                self.winning_five = find_winning_line(self.board, row, col, self.board_size)
                print(f"玩家{self.current_player}获胜！")
            else:
                # 切换玩家
                self.current_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
            
            return True
        return False
    
    def undo_move(self):
        """撤回一步棋"""
        if len(self.move_history) > 0:
            # 从历史记录中取出最后一步
            row, col, player = self.move_history.pop()
            
            # 保存到恢复栈
            self.undo_stack.append((row, col, player))
            
            # 清空棋盘位置
            self.board[row][col] = PIECE_EMPTY
            
            # 重置获胜状态
            self.winner = 0
            self.winning_five = []
            
            # 恢复当前玩家
            self.current_player = player
            
            return True
        return False
    
    def redo_move(self):
        """恢复一步棋"""
        if len(self.undo_stack) > 0:
            # 从恢复栈中取出最后一步
            row, col, player = self.undo_stack.pop()
            
            # 将棋子放回棋盘
            piece = PIECE_BLACK if player == PLAYER_BLACK else PIECE_WHITE
            self.board[row][col] = piece
            
            # 添加回历史记录
            self.move_history.append((row, col, player))
            
            # 检查是否获胜
            if check_winner_at_position(self.board, row, col, self.board_size):
                self.winner = player
                self.winning_five = find_winning_line(self.board, row, col, self.board_size)
            
            # 设置下一个玩家
            self.current_player = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
            
            return True
        return False
    
    def ai_move(self):
        """AI进行移动"""
        if self.winner != 0 or self.ai_player.thinking:
            return
        
        print("AI开始思考...")
        
        # 更新显示，显示"AI思考中..."
        self.ui.draw_background(self.screen)
        self.ui.draw_board(self.screen, self.board_size)
        self.ui.draw_pieces(self.screen, self.board, self.winning_five, self.board_size)
        self.ui.draw_game_info(self.screen, self.current_player, self.winner, 
                              self.move_history, self.undo_stack, True, self.player_side)
        pygame.display.flip()
        
        try:
            # 调用AI函数计算落子位置
            row, col = self.ai_player.get_move(self.board, self.board_size)
            
            # 验证位置有效性
            if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == PIECE_EMPTY:
                if self.place_piece(row, col):
                    print(f"AI在({row},{col})下棋成功")
                else:
                    print("AI下棋失败")
            else:
                print(f"AI返回无效位置({row},{col})")
                
        except Exception as e:
            print(f"AI移动出错: {e}")
    
    def handle_menu_events(self, event):
        """处理菜单事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.game_state = GAME_STATE_SELECT_SIZE  # 进入棋盘大小选择
    
    def handle_size_selection_events(self, event):
        """处理棋盘大小选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            buttons = self.ui.draw_size_selection(self.screen)
            mouse_pos = pygame.mouse.get_pos()
            for idx, rect in enumerate(buttons):
                if rect.collidepoint(mouse_pos):
                    self.board_size = 13 + idx  # 13, 14, 15
                    print(f"选择棋盘大小: {self.board_size}x{self.board_size}")
                    self.reset_game()
                    self.game_state = GAME_STATE_SELECT_SIDE
                    break
    
    def handle_side_selection_events(self, event):
        """处理执棋方选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            button1_rect, button2_rect = self.ui.draw_side_selection(self.screen)
            mouse_pos = pygame.mouse.get_pos()
            if button1_rect.collidepoint(mouse_pos):
                # 玩家选择黑方（先手）
                self.player_side = PLAYER_BLACK
                print("玩家选择执黑先行")
                self.reset_game()
                self.game_state = GAME_STATE_PLAYING
            elif button2_rect.collidepoint(mouse_pos):
                # 玩家选择白方（后手）
                self.player_side = PLAYER_WHITE
                print("玩家选择执白后行")
                self.reset_game()
                self.game_state = GAME_STATE_PLAYING
                pygame.time.wait(500)
                self.ai_move()
    
    def handle_game_events(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.ai_player.thinking and self.winner == 0:
                # 只有在玩家回合才能下棋
                if self.current_player == self.player_side:
                    row, col = get_board_position_from_mouse(event.pos, self.ui.board_x, self.ui.board_y, self.board_size)
                    if row is not None and col is not None:
                        if self.place_piece(row, col):
                            print(f"玩家在({row},{col})下棋成功")
        
        elif event.type == pygame.KEYDOWN:
            current_time = pygame.time.get_ticks()
            
            # 防止按键重复触发
            if (event.key in self.last_key_time and 
                current_time - self.last_key_time[event.key] < 300):
                return
            
            self.last_key_time[event.key] = current_time
            
            if event.key == pygame.K_r:  # R键重新开始
                print("R键 - 重新开始游戏")
                self.reset_game()
                if self.player_side == PLAYER_WHITE:
                    pygame.time.wait(500)
                    self.ai_move()
                
            elif event.key == pygame.K_m:  # M键返回菜单
                print("M键 - 返回菜单")
                self.game_state = GAME_STATE_MENU
                
            elif event.key == pygame.K_u:  # U键撤回
                if not self.ai_player.thinking and len(self.move_history) > 0 and self.winner == 0:
                    # 撤回两步（玩家的一步 + AI的一步）
                    moves_to_undo = min(2, len(self.move_history))
                    for _ in range(moves_to_undo):
                        if not self.undo_move():
                            break
                    print(f"撤回了{moves_to_undo}步")
                else:
                    print("无法撤回：AI思考中、无历史记录或游戏已结束")
                    
            elif event.key == pygame.K_d:  # D键恢复
                if not self.ai_player.thinking and len(self.undo_stack) > 0 and self.winner == 0:
                    # 恢复两步
                    moves_to_redo = min(2, len(self.undo_stack))
                    for _ in range(moves_to_redo):
                        if not self.redo_move():
                            break
                    print(f"恢复了{moves_to_redo}步")
                else:
                    print("无法恢复：AI思考中、无恢复记录或游戏已结束")
            
            elif event.key == pygame.K_ESCAPE:  # ESC键返回菜单
                print("ESC键 - 返回菜单")
                self.game_state = GAME_STATE_MENU
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif self.game_state == GAME_STATE_MENU:
                    self.handle_menu_events(event)
                
                elif self.game_state == GAME_STATE_SELECT_SIZE:
                    self.handle_size_selection_events(event)
                
                elif self.game_state == GAME_STATE_SELECT_SIDE:
                    self.handle_side_selection_events(event)
                
                elif self.game_state == GAME_STATE_PLAYING:
                    self.handle_game_events(event)
            
            # 绘制
            if self.game_state == GAME_STATE_MENU:
                self.ui.draw_menu(self.screen)
            
            elif self.game_state == GAME_STATE_SELECT_SIZE:
                self.ui.draw_size_selection(self.screen)
            
            elif self.game_state == GAME_STATE_SELECT_SIDE:
                self.ui.draw_side_selection(self.screen)
            
            elif self.game_state == GAME_STATE_PLAYING:
                self.ui.draw_background(self.screen)
                self.ui.draw_board(self.screen, self.board_size)
                self.ui.draw_pieces(self.screen, self.board, self.winning_five, self.board_size)
                self.ui.draw_game_info(self.screen, self.current_player, self.winner, 
                                      self.move_history, self.undo_stack, 
                                      self.ai_player.thinking, self.player_side)
                
                # AI回合处理
                if (self.current_player != self.player_side and
                        self.winner == 0 and
                        not self.ai_player.thinking):
                    pygame.time.wait(40)
                    self.ai_move()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


    