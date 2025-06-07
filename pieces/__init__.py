"""棋子模块

定义棋子类型
"""

from .chess_pieces import (
    Piece, Pawn
)

__all__ = [
    'Piece',       # 基类
    'Pawn',        # 棋子初始类型
]