from panda3d.core import BitMask32, LineSegs
from utils.constants import (
    BOARD_SIZE, TOTAL_SQUARES, SQUARE_SCALE, WHITE_BOX_POS, BLACK_BOX_POS, BOX_SIZE,
    DECORATION_POSITION_OFFSET, DECORATION_SCALE_X, DECORATION_SCALE_Y, DECORATION_SCALE_Z, DECORATION_ROTATION,
    WHITE_3D, PIECEBLACK,
    THICKNESS_POSITION_OFFSET, THICKNESS_SCALE,
    OPPONENT_MODEL_POSITION, OPPONENT_MODEL_SCALE, OPPONENT_MODEL_ROTATION
)
from utils.helpers import square_pos, square_color

class BoardSetup:
    def __init__(self, loader, render, opponent_model_path="models/Raiden shogun.bam",opponent_model_position=OPPONENT_MODEL_POSITION):
        self.loader = loader
        self.render = render
        self.opponent_model_path = opponent_model_path
        self.opponent_model_position = opponent_model_position
        self.squares = [None for _ in range(TOTAL_SQUARES)]
        self.square_root = None
        self.white_box = None
        self.black_box = None
        self.deco_white = None
        self.deco_black = None
        self.thickness_model = None
        self.opponent_model = None

    def setup_board(self):
        """创建棋盘格子和外观装饰"""
        self.square_root = self.render.attachNewNode("squareRoot")
        # 棋盘格子
        for i in range(TOTAL_SQUARES):
            square = self.loader.loadModel("models/square")
            square.reparentTo(self.square_root)
            square.setPos(square_pos(i))
            square.setColor(square_color(i))
            square.setScale(SQUARE_SCALE)
            square.find("**/polygon").node().setIntoCollideMask(BitMask32.bit(1))
            square.find("**/polygon").node().setTag('square', str(i))
            square.setScale(square.getScale()[0], square.getScale()[1], 0.1)
            self.squares[i] = square
        # 网格线
        self._draw_gomoku_grid()
        # 棋盒
        self._setup_piece_boxes()
        # 棋盘厚度和对手模型等装饰
        self._load_board_decorations()

    def _draw_gomoku_grid(self):
        """绘制棋盘网格线"""
        lines = LineSegs()
        lines.setThickness(1.5)
        lines.setColor(0, 0, 0, 1)
        grid_range = 7 * SQUARE_SCALE
        for row in range(BOARD_SIZE):
            y_pos = grid_range - row * SQUARE_SCALE
            lines.moveTo(-grid_range, y_pos, 0.01)
            lines.drawTo(grid_range, y_pos, 0.01)
        for col in range(BOARD_SIZE):
            x_pos = -grid_range + col * SQUARE_SCALE
            lines.moveTo(x_pos, grid_range, 0.01)
            lines.drawTo(x_pos, -grid_range, 0.01)
        grid_node = self.render.attachNewNode(lines.create())
        grid_node.reparentTo(self.square_root)

    def _setup_piece_boxes(self):
        """创建棋盒及其装饰"""
        # 白棋盒
        self.white_box = self.loader.loadModel("models/square")
        self.white_box.reparentTo(self.square_root)  # 挂到square_root
        self.white_box.setPos(WHITE_BOX_POS)
        self.white_box.setTransparency(True)
        self.white_box.setColor(1, 1, 1, 0)
        self.white_box.setScale(BOX_SIZE, BOX_SIZE, 0.2)
        polygon_node = self.white_box.find("**/polygon")
        if polygon_node:
            polygon_node.node().setIntoCollideMask(BitMask32.bit(1))
            polygon_node.node().setTag('piece_box', 'white')
        # 白棋盒装饰
        self.deco_white = self.loader.loadModel("models/qihe.obj")
        if self.deco_white:
            self.deco_white.reparentTo(self.square_root)  # 挂到square_root
            self.deco_white.setPos(
                WHITE_BOX_POS[0] + DECORATION_POSITION_OFFSET[0],
                WHITE_BOX_POS[1] + DECORATION_POSITION_OFFSET[1],
                WHITE_BOX_POS[2] + DECORATION_POSITION_OFFSET[2]
            )
            self.deco_white.setScale(DECORATION_SCALE_X, DECORATION_SCALE_Y, DECORATION_SCALE_Z)
            self.deco_white.setHpr(*DECORATION_ROTATION)
            self.deco_white.setColor(WHITE_3D)
        # 黑棋盒
        self.black_box = self.loader.loadModel("models/square")
        self.black_box.reparentTo(self.square_root)  # 挂到square_root
        self.black_box.setPos(BLACK_BOX_POS)
        self.black_box.setTransparency(True)
        self.black_box.setColor(1, 1, 1, 0)
        self.black_box.setScale(BOX_SIZE, BOX_SIZE, 0.2)
        polygon_node = self.black_box.find("**/polygon")
        if polygon_node:
            polygon_node.node().setIntoCollideMask(BitMask32.bit(1))
            polygon_node.node().setTag('piece_box', 'black')
        # 黑棋盒装饰
        self.deco_black = self.loader.loadModel("models/qihe.obj")
        if self.deco_black:
            self.deco_black.reparentTo(self.square_root)  # 挂到square_root
            self.deco_black.setPos(
                BLACK_BOX_POS[0] + DECORATION_POSITION_OFFSET[0],
                BLACK_BOX_POS[1] + DECORATION_POSITION_OFFSET[1],
                BLACK_BOX_POS[2] + DECORATION_POSITION_OFFSET[2]
            )
            self.deco_black.setScale(DECORATION_SCALE_X, DECORATION_SCALE_Y, DECORATION_SCALE_Z)
            self.deco_black.setHpr(*DECORATION_ROTATION)
            self.deco_black.setColor(PIECEBLACK)

    def _load_board_decorations(self):
        """棋盘厚度、对手模型等装饰"""
        # 棋盘厚度
        self.thickness_model = self.loader.loadModel("models/qi_pan.obj")
        if self.thickness_model:
            self.thickness_model.reparentTo(self.square_root)
            self.thickness_model.setPos(*THICKNESS_POSITION_OFFSET)
            self.thickness_model.setScale(
                BOARD_SIZE * SQUARE_SCALE * THICKNESS_SCALE[0],
                BOARD_SIZE * SQUARE_SCALE * THICKNESS_SCALE[1],
                THICKNESS_SCALE[2]
            )
            self.thickness_model.setColor(0.71, 0.55, 0.35, 1)
        # 对手模型
        self.opponent_model = self.loader.loadModel(self.opponent_model_path)
        if self.opponent_model:
            self.opponent_model.reparentTo(self.square_root)
            self.opponent_model.setPos(*self.opponent_model_position)
            self.opponent_model.setScale(*OPPONENT_MODEL_SCALE)
            self.opponent_model.setHpr(*OPPONENT_MODEL_ROTATION)

    def cleanup(self):
        """清理棋盘和装饰节点"""
        if self.square_root:
            self.square_root.removeNode()
            self.square_root = None
        # 如果棋盒和装饰单独挂在render下，也要清理
        if hasattr(self, "white_box") and self.white_box:
            self.white_box.removeNode()
            self.white_box = None
        if hasattr(self, "black_box") and self.black_box:
            self.black_box.removeNode()
            self.black_box = None
        if hasattr(self, "deco_white") and self.deco_white:
            self.deco_white.removeNode()
            self.deco_white = None
        if hasattr(self, "deco_black") and self.deco_black:
            self.deco_black.removeNode()
            self.deco_black = None
        if hasattr(self, "thickness_model") and self.thickness_model:
            self.thickness_model.removeNode()
            self.thickness_model = None
        if hasattr(self, "opponent_model") and self.opponent_model:
            self.opponent_model.removeNode()
            self.opponent_model = None