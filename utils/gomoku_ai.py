from abc import ABC, abstractmethod
from utils.chessboard import ChessBoard

class GomokuAI:

    def get_next_chessboard(self, input_chessboard: ChessBoard, player_side: int) -> ChessBoard:
        """获取AI的下一步棋盘状态"""
        raise NotImplementedError("This method should be overridden by subclasses")