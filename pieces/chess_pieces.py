"""国际象棋棋子类定义"""

from utils.helpers import square_pos

class Piece(object):
    """棋子基类"""
    def __init__(self, square, color, base_instance):
        self.square = square
        self.base = base_instance
        self.obj = self.base.loader.loadModel(self.model)
        self.obj.reparentTo(self.base.render)
        self.obj.setColor(color)
        self.obj.setPos(square_pos(square))

class Pawn(Piece):
    model = "models/white_chess_piece.obj"

    def __init__(self, square_index, color, base):
        super().__init__(square_index, color, base)
        self.obj.setScale(0.3, 0.3, 0.3)  # 缩小模型
        self.obj.setHpr(0, -90, 0)       # 调整方向

class King(Piece):
    model = "models/king"

class Queen(Piece):
    model = "models/queen"

class Bishop(Piece):
    model = "models/bishop"

class Knight(Piece):
    model = "models/knight"

class Rook(Piece):
    model = "models/rook"

# 棋子顺序(从白方视角)
PIECE_ORDER = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)