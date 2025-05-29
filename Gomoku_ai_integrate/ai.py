"""
AI相关功能
"""
import time
from constants import *
from config_4 import *

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

def check_win_all(board_inner):
    """检查所有方向的获胜情况"""
    board_c = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_c[x + y].append(board_inner[x][y])
    
    board_d = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_d[x - y].append(board_inner[x][y])
    
    return [check_win(board_inner), 
            check_win([list(i) for i in zip(*board_inner)]), 
            check_win(board_c),
            check_win(board_d)]

def value(board_inner, temp_list, value_model, chr):
    """评估棋型价值"""
    score = 0
    num = 0
    for list_str in board_inner:
        str_line = ''.join(list_str)
        for key in value_model:
            for pattern_name, (pattern, pattern_score) in value_model[key]:
                count = str_line.count(pattern)
                if count > 0:
                    temp_list.append((num, (pattern_name, pattern, pattern_score), count))
                    score += pattern_score * count
        num += 1
    return score

def additional(te_list):
    """额外评分计算"""
    score = 0
    temp_list = [i[1][0][:2] for i in te_list]
    if sum([temp_list.count(i) for i in ['4_', '3p']]) >= 2:
        score += 30
    elif sum([temp_list.count(i) for i in ['3p', '3_']]) >= 2 and sum([temp_list.count(i) for i in ['3p']]) > 0:
        score += 15
    return score

def value_all(board_inner, temp_list, value_model, chr):
    """计算所有方向的评分"""
    board_c = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_c[x + y].append(board_inner[x][y])
    
    board_d = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_d[x - y].append(board_inner[x][y])
    
    a = value(board_inner, temp_list, value_model, chr)
    b = value([list(i) for i in zip(*board_inner)], temp_list, value_model, chr)
    c = value(board_c, temp_list, value_model, chr)
    d = value(board_d, temp_list, value_model, chr)
    add = additional(temp_list)
    return a + b + c + d + add

def value_chess(board_inner):
    """AI决策主函数"""
    t1 = time.time()
    if board_inner == [[PIECE_EMPTY] * 15 for _ in range(15)]:
        return 7, 7, 0

    temp_list_x = []
    temp_list_o = []
    tp_list_x_2 = []
    tp_list_o_2 = []
    tp_list_d = []
    score_x = value_all(board_inner, temp_list_x, value_model_X, PIECE_BLACK)
    pos_x = (0, 0)
    score_o = value_all(board_inner, temp_list_o, value_model_O, PIECE_WHITE)
    pos_o = (0, 0)
    pos_d = (0, 0)
    score_x_2 = 0
    score_o_2 = 0
    score_diff = 0

    chess_range_x = [x for x in range(15) if ''.join(board_inner[x]).replace(' ', '') != '']
    chess_range_y = [y for y in range(15) if ''.join([list(i) for i in zip(*board_inner)][y]).replace(' ', '') != '']
    
    if chess_range_x and chess_range_y:
        range_x = (max(0, min(chess_range_x) - 2), min(max(chess_range_x) + 2, 15))
        range_y = (max(0, min(chess_range_y) - 2), min(max(chess_range_y) + 2, 15))
    else:
        range_x = (0, 15)
        range_y = (0, 15)
    
    num = 0

    for x in range(*range_x):
        for y in range(*range_y):
            tp_list_x = []
            tp_list_o = []
            tp_list_c = []
            if board_inner[x][y] != PIECE_EMPTY:
                continue
            else:
                num += 1
                board_inner[x][y] = PIECE_BLACK
                score_a = value_all(board_inner, tp_list_x, value_model_X, PIECE_BLACK)
                score_c = value_all(board_inner, tp_list_c, value_model_O, PIECE_WHITE)
                if score_a > score_x_2:
                    pos_x = x, y
                    tp_list_x_2 = tp_list_x
                    score_x_2 = score_a

                board_inner[x][y] = PIECE_WHITE
                score_b = value_all(board_inner, tp_list_o, value_model_O, PIECE_WHITE)
                if score_b > score_o_2:
                    pos_o = x, y
                    tp_list_o_2 = tp_list_o
                    score_o_2 = score_b

                board_inner[x][y] = PIECE_EMPTY
                diff = 1.1 * (score_a - score_x) + score_o - score_c + score_b - score_c
                if diff > score_diff:
                    pos_d = x, y
                    tp_list_d = tp_list_x
                    score_diff = diff

    if score_x_2 >= 1000:
        score = score_x_2
        pos = pos_x
    elif score_o_2 >= 1000:
        pos = pos_o
        x, y = pos
        board_inner[x][y] = PIECE_BLACK
        temp_list_x.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, PIECE_BLACK)
        board_inner[x][y] = PIECE_EMPTY
    else:
        pos = pos_d
        x, y = pos
        board_inner[x][y] = PIECE_BLACK
        temp_list_x.clear()
        temp_list_o.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, PIECE_BLACK)
        board_inner[x][y] = PIECE_EMPTY

    return pos[0], pos[1], score

class AIPlayer:
    """AI玩家类"""
    
    def __init__(self):
        self.thinking = False
    
    def get_move(self, board):
        """获取AI的下一步移动"""
        self.thinking = True
        try:
            row, col, score = value_chess(board)
            print(f"AI计算结果: ({row}, {col}), 评分: {score}")
            return row, col
        except Exception as e:
            print(f"AI计算出错: {e}")
            return self._get_fallback_move(board)
        finally:
            self.thinking = False
    
    def _get_fallback_move(self, board):
        """获取备用移动位置"""
        # 寻找中心附近的空位
        center = 7
        for radius in range(8):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r, c = center + dr, center + dc
                    if (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                        board[r][c] == PIECE_EMPTY):
                        return r, c
        return 0, 0  # 最后的备用位置