""" 
AI相关功能 - Minimax版本
"""
import math
from utils.constants import *
from utils.chessboard import ChessBoard
from utils.gomoku_ai import GomokuAI
from utils.minimax_ai_engine import MinimaxAIEngine

class MinimaxAIPlayer(GomokuAI):
    """基于Minimax算法的AI玩家"""
    
    def __init__(self, depth=3):
        self.thinking = False
        self.depth = depth
        self.engine = MinimaxAIEngine(depth)
    
    def convert_board(self, board, player_side):
        """将框架棋盘转换为Minimax引擎的内部表示"""
        converted = []
        for row in board:
            converted_row = []
            for cell in row:
                if cell == PIECE_EMPTY:
                    converted_row.append(0)
                elif cell == PIECE_BLACK:
                    # 根据AI角色决定表示
                    converted_row.append(1 if player_side == PLAYER_BLACK else -1)
                elif cell == PIECE_WHITE:
                    converted_row.append(-1 if player_side == PLAYER_BLACK else 1)
            converted.append(converted_row)
        return converted
    
    def get_next_chessboard(self, chessboard: ChessBoard, player_side: int) -> ChessBoard:
        """获取AI的下一步棋盘状态"""
        if chessboard.winner != 0:
            return chessboard
        
        board_size = chessboard.size
        board_inner = chessboard.board
        
        # AI计算下一步
        row, col = self.get_move(board_inner, board_size, player_side)
        
        # 根据player_side确定棋子类型
        piece_type = PIECE_BLACK if player_side == PLAYER_BLACK else PIECE_WHITE
        
        # 更新棋盘状态
        if 0 <= row < board_size and 0 <= col < board_size and board_inner[row][col] == PIECE_EMPTY:
            chessboard.place_stone(row, col, player_side)
        
        return chessboard
    
    def get_move(self, board, board_size, player_side):
        """获取AI的下一步移动"""
        self.thinking = True
        try:
            # 转换棋盘表示
            converted_board = self.convert_board(board, player_side)
            
            # 初始化引擎
            self.engine = MinimaxAIEngine(self.depth)
            self.engine.board_size = board_size
            self.engine.boardMap = converted_board
            
            # 如果是空棋盘，直接返回中心点
            if all(cell == 0 for row in converted_board for cell in row):
                center = board_size // 2
                return center, center
            
            # 初始化边界
            self.engine.nextBound = {}
            for i in range(board_size):
                for j in range(board_size):
                    if converted_board[i][j] != 0:
                        self.engine.updateBound(i, j, self.engine.nextBound)
            
            # 执行搜索
            self.engine.alphaBetaPruning(
                self.engine.depth,
                self.engine.boardValue,
                self.engine.nextBound,
                -math.inf,
                math.inf,
                True
            )
            
            row, col = self.engine.currentI, self.engine.currentJ
            print(f"Minimax AI计算结果: ({row}, {col}), 评分: {self.engine.boardValue}")
            return row, col
        except Exception as e:
            print(f"Minimax AI计算出错: {e}")
            return self._get_fallback_move(board, board_size)
        finally:
            self.thinking = False
    
    def _get_fallback_move(self, board, board_size):
        """备用策略：在棋盘上寻找空位置"""
        center = board_size // 2
        for radius in range(board_size // 2 + 1):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r, c = center + dr, center + dc
                    if (0 <= r < board_size and 0 <= c < board_size and 
                        board[r][c] == PIECE_EMPTY):
                        return r, c
        return 0, 0
