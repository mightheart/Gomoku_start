from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from constants import PIECE_EMPTY, PIECE_BLACK, PIECE_WHITE, PLAYER_BLACK, PLAYER_WHITE

class ChessBoard(BaseModel):
    size: int = Field(default=15, description="棋盘大小")
    board: List[List[str]] = Field(default_factory=list, description="棋盘二维数组")
    move_history: List[Tuple[int, int, int]] = Field(default_factory=list, description="落子历史")
    undo_stack: List[Tuple[int, int, int]] = Field(default_factory=list, description="撤回栈")
    winner: int = Field(default=0, description="获胜者")
    winning_line: List[Tuple[int, int]] = Field(default_factory=list, description="获胜连线")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.board:
            self.board = [[PIECE_EMPTY for _ in range(self.size)] for _ in range(self.size)]
    
    def place_stone(self, row: int, col: int, player: int) -> bool:
        """在指定位置放置棋子"""
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == PIECE_EMPTY:
            piece = PIECE_BLACK if player == PLAYER_BLACK else PIECE_WHITE
            self.board[row][col] = piece
            
            # 记录落子历史
            self.move_history.append((row, col, player))
            
            # 清空恢复栈
            self.undo_stack = []
            
            # 检查是否获胜
            if self.check_winner_at_position(row, col):
                self.winner = player
                self.winning_line = self.find_winning_line(row, col)
            
            return True
        return False
    
    def check_winner_at_position(self, row: int, col: int) -> bool:
        """检查指定位置是否形成五子连珠"""
        player = self.board[row][col]
        if player == PIECE_EMPTY:
            return False
        
        directions = [
            (0, 1), (1, 0), (1, 1), (1, -1)
        ]
        
        for dr, dc in directions:
            count = 1
            # 向正方向检查
            r, c = row + dr, col + dc
            while (0 <= r < self.size and 0 <= c < self.size and 
                   self.board[r][c] == player):
                count += 1
                r, c = r + dr, c + dc
            
            # 向负方向检查
            r, c = row - dr, col - dc
            while (0 <= r < self.size and 0 <= c < self.size and 
                   self.board[r][c] == player):
                count += 1
                r, c = r - dr, c - dc
            
            if count >= 5:
                return True
        return False
    
    def find_winning_line(self, row: int, col: int) -> List[Tuple[int, int]]:
        """找到获胜的连线"""
        player = self.board[row][col]
        directions = [
            (0, 1), (1, 0), (1, 1), (1, -1)
        ]
        
        for dr, dc in directions:
            line = [(row, col)]
            
            # 向正方向收集
            r, c = row + dr, col + dc
            while (0 <= r < self.size and 0 <= c < self.size and 
                   self.board[r][c] == player):
                line.append((r, c))
                r, c = r + dr, c + dc
            
            # 向负方向收集
            r, c = row - dr, col - dc
            while (0 <= r < self.size and 0 <= c < self.size and 
                   self.board[r][c] == player):
                line.insert(0, (r, c))
                r, c = r - dr, c - dc
            
            if len(line) >= 5:
                return line[:5]
        
        return []
    
    def undo_move(self) -> Optional[Tuple[int, int, int]]:
        """撤回一步棋"""
        if len(self.move_history) > 0:
            # 从历史记录中取出最后一步
            row, col, player = self.move_history.pop()
            
            # 保存到恢复栈
            self.undo_stack.append((row, col, player))
            
            # 清空棋盘位置
            self.board[row][col] = PIECE_EMPTY
            
            # 重置赢家信息
            self.winner = 0
            self.winning_line = []
            
            return (row, col, player)
        return None
    
    def redo_move(self) -> Optional[Tuple[int, int, int]]:
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
            if self.check_winner_at_position(row, col):
                self.winner = player
                self.winning_line = self.find_winning_line(row, col)
            
            return (row, col, player)
        return None
    
    def is_empty(self, row: int, col: int) -> bool:
        """检查指定位置是否为空"""
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == PIECE_EMPTY
    
    def get_stone(self, row: int, col: int) -> str:
        """获取指定位置的棋子"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.board[row][col]
        return ''
    
    def clear_board(self):
        """清空棋盘"""
        self.board = [[PIECE_EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.move_history = []
        self.undo_stack = []
        self.winner = 0
        self.winning_line = []
    
    def get_player_from_piece(self, piece: str) -> int:
        """根据棋子符号获取玩家标识"""
        if piece == PIECE_BLACK:
            return PLAYER_BLACK
        elif piece == PIECE_WHITE:
            return PLAYER_WHITE
        return 0
    
    def has_moves_to_undo(self) -> bool:
        """检查是否有可撤回的步数"""
        return len(self.move_history) > 0
    
    def has_moves_to_redo(self) -> bool:
        """检查是否有可恢复的步数"""
        return len(self.undo_stack) > 0
