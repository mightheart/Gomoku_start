"""
AI相关功能
"""
import time
from utils.constants import *
from utils.config_4 import *
from utils.chessboard import ChessBoard
from utils.gomoku_ai import GomokuAI

def set_chess(board_inner, x, y, chr):
    """设置棋子"""
    if board_inner[x][y] != PIECE_EMPTY:
        return False
    else:
        board_inner[x][y] = chr
        return True

def check_win(board_inner):
    """检查是否获胜"""
    for list_str in board_inner:
        str_line = ''.join(list_str)
        if 'XXXXX' in str_line or 'OOOOO' in str_line:
            return True
    return False




class AIPlayer(GomokuAI):
    """AI玩家类"""
    
    def __init__(self):
        self.thinking = False
    
    def get_next_chessboard(self, chessboard: ChessBoard, player_side: int) -> ChessBoard:
        """获取AI的下一步棋盘状态"""
        if chessboard.winner != 0:
            return chessboard
        
        board_size = chessboard.size
        board_inner = chessboard.board
        
        # AI计算下一步
        row, col = self.get_move(board_inner, board_size)
        
        # 根据player_side确定棋子类型
        piece_type = PIECE_BLACK if player_side == PLAYER_BLACK else PIECE_WHITE
        
        # 更新棋盘状态
        if set_chess(board_inner, row, col, piece_type):
            chessboard.place_stone(row, col, player_side)
        
        return chessboard
    
    
    def get_move(self, board, board_size):
        """获取AI的下一步移动"""
        self.thinking = True
        try:
            row, col, score = value_chess(board, board_size)
            print(f"AI计算结果: ({row}, {col}), 评分: {score}")
            return row, col
        except Exception as e:
            print(f"AI计算出错: {e}")
            return self._get_fallback_move(board, board_size)
        finally:
            self.thinking = False
    
    def _get_fallback_move(self, board, board_size):
        """获取备用移动位置"""
        center = board_size // 2
        for radius in range(board_size // 2 + 1):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r, c = center + dr, center + dc
                    if (0 <= r < board_size and 0 <= c < board_size and 
                        board[r][c] == PIECE_EMPTY):
                        return r, c
        return 0, 0  # 最后的备用位置