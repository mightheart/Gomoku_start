"""辅助函数"""
from .constants import TOTAL_SQUARES, BOARD_SIZE
from panda3d.core import LPoint3
import math  # 添加数学函数支持

def point_at_z(z, point, vec):
    """
    给定一条线(向量加原点)和期望的z值，返回线上z值为指定值的点
    用于根据2D鼠标位置确定3D空间中的位置
    """
    return point + vec * ((z - point.getZ()) / vec.getZ())

def square_pos(i):
    """获取棋盘格子i的3D位置 - 15x15棋盘"""
    from .constants import SQUARE_SCALE, BOARD_SIZE
    row = i // BOARD_SIZE
    col = i % BOARD_SIZE
    # 中心对齐：从-7到+7的位置
    x = (col - 7) * SQUARE_SCALE
    y = (7 - row) * SQUARE_SCALE  # Y轴翻转
    return LPoint3(x, y, 0)

def square_color(i):
    """设定棋盘颜色"""
    from .constants import WOOD_MEDIUM
    return WOOD_MEDIUM
    # """确定棋盘格子i应该是白色还是黑色"""
    # from .constants import WOOD_LIGHT, WOOD_DARK
    # if (i + ((i // 8) % 2)) % 2:
    #     return WOOD_DARK
    # else:
    #     return WOOD_LIGHT

def gomoku_pos_to_square(row, col):
    """将五子棋行列坐标转换为数组索引 - 15x15"""
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row * BOARD_SIZE + col
    return -1  # 无效位置

def square_to_gomoku_pos(square_index):
    """将数组索引转换为五子棋行列坐标 - 15x15"""
    if 0 <= square_index < BOARD_SIZE * BOARD_SIZE:
        row = square_index // BOARD_SIZE
        col = square_index % BOARD_SIZE
        return (row, col)
    return (-1, -1)  # 无效位置

def _piece_color_match(piece, target_color):
    """检查棋子颜色是否匹配"""
    from .constants import WHITE, PIECEBLACK
    piece_color = piece.obj.getColor()
    
    if target_color == WHITE:
        return piece_color[0] > 0.5  # 白色棋子R分量较高
    else:
        return piece_color[0] < 0.5  # 黑色棋子R分量较低

def is_valid_board_position(square_index):
    """检查是否是有效的棋盘位置 - 15x15"""
    return 0 <= square_index < 225

def check_five_in_row(pieces, last_pos, color):
    """检查是否有五子连线"""
    if last_pos < 0 or last_pos > TOTAL_SQUARES - 1:
        return False
    
    row, col = square_to_gomoku_pos(last_pos)
    if row == -1:
        return False
    
    # 检查四个方向：水平、垂直、对角线1、对角线2
    directions = [
        (0, 1),   # 水平
        (1, 0),   # 垂直
        (1, 1),   # 主对角线
        (1, -1)   # 副对角线
    ]
    
    for dr, dc in directions:
        if _count_line(pieces, row, col, dr, dc, color) >= 5:
            return True
    
    return False

def _count_line(pieces, row, col, dr, dc, color):
    """计算指定方向上连续的同色棋子数量 - 15x15"""
    count = 1  # 包括当前棋子
    
    # 正方向计数
    r, c = row + dr, col + dc
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        pos = gomoku_pos_to_square(r, c)
        if pos != -1 and pieces[pos] and _piece_color_match(pieces[pos], color):
            count += 1
            r, c = r + dr, c + dc
        else:
            break
    
    # 负方向计数
    r, c = row - dr, col - dc
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        pos = gomoku_pos_to_square(r, c)
        if pos != -1 and pieces[pos] and _piece_color_match(pieces[pos], color):
            count += 1
            r, c = r - dr, c - dc
        else:
            break
    
    return count

def _get_piece_name(piece):
    """获取棋子的可读名称（用于调试）"""
    if not piece:
        return "Empty"
    
    color = "白" if piece.obj.getColor()[0] > 0.5 else "黑"
    return f"{color}子"