"""棋子模块

定义国际象棋中的各种棋子类型
"""

from .chess_pieces import (
    Piece, Pawn, King, Queen, Bishop, Knight, Rook,
    PIECE_ORDER
)

__all__ = [
    'Piece',       # 基类
    'Pawn',        # 兵
    'King',        # 王
    'Queen',       # 后
    'Bishop',      # 象
    'Knight',      # 马
    'Rook',        # 车
    'PIECE_ORDER'  # 棋子顺序
]