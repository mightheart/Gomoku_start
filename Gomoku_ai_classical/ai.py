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


def value(board_inner, temp_list, value_model, chr,board_size):
    score = 0
    num = 0
    for list_str in board_inner:
        if ''.join(list_str).count(chr) < 2:
            continue
        a = 0
        for i in range(board_size-4):
            if a == 0:
                temp = []
                for j in range(5, 12):
                    if i + j > len(list_str):
                        break
                    num += 1
                    s = ''.join(list_str[i:i + j])
                    s_num = min(s.count(chr), 5)
                    if s_num < 2:
                        continue
                    else:
                        if i == 0:
                            for k in [t for _ in value_model[0].items() for t in _[1] if int(_[0]) <= s_num]:
                                if s == k[1][0]:
                                    temp.append((i, k))
                        else:
                            if i + j < len(list_str):
                                for k in [t for _ in value_model[1].items() for t in _[1] if int(_[0]) <= s_num]:
                                    if s == k[1][0]:
                                        temp.append((i, k))
                            elif i + j == len(list_str):
                                for k in [t for _ in value_model[2].items() for t in _[1] if int(_[0]) <= s_num]:
                                    if s == k[1][0]:
                                        temp.append((i, k))
            else:
                a -= 1
                temp = []
            if temp:
                max_value = max([i[1][1][1] for i in temp])
                max_shape = [i for i in temp if i[1][1][1] == max_value][0]
                if max_shape[1][0] in ['4_1_e', '4_1_1',
                                       '4_2_5', '4_2_6', '4_2_7', '4_2_8_e', '4_2_9',
                                       '4_3_4_s',
                                       '3p_0', '3p_0_1',
                                       '3p_1_3', '3_1_4_e', '3_1_5',
                                       '3_2_5_s',
                                       '3_3', '3_3_1', '3_3_2_e', '3_3_3',
                                       '2_0_5',
                                       '2_1',
                                       '2_2_1', '2_2_2_e', '2_2_3']:
                    a = 1
                elif max_shape[1][0] in ['4_2_1', '4_2_2', '4_2_3_e', '4_2_4',
                                         '4_3', '4_3_8', '4_3_9',
                                         '3p_1', '3_1_1_e', '3_1_2',
                                         '2_0',
                                         '2_2']:
                    a = 2
                elif max_shape[1][0] in ['3p_2']:
                    a = 3
                elif max_shape[1][0] in ['4_2']:
                    a = 5
                temp_list.append(max_shape)
                score += max_value
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

def value_all(board_inner, temp_list, value_model, chr, board_size):
    """计算所有方向的评分"""
    board_c = [[] for _ in range(board_size*2-1)]
    for x in range(board_size):
        for y in range(board_size):
            board_c[x + y].append(board_inner[x][y])
    board_d = [[] for _ in range(board_size*2-1)]
    for x in range(board_size):
        for y in range(board_size):
            board_d[x - y].append(board_inner[x][y])
    a = value(board_inner, temp_list, value_model, chr,board_size)
    b = value([list(i) for i in zip(*board_inner)], temp_list, value_model, chr,board_size)
    c = value(board_c, temp_list, value_model, chr,board_size)
    d = value(board_d, temp_list, value_model, chr,board_size)
    add = additional(temp_list)
    return a + b + c + d + add

def value_chess(board_inner, board_size):
    """AI决策主函数"""
    t1 = time.time()
    if board_inner == [[PIECE_EMPTY] * board_size for _ in range(board_size)]:
        return board_size // 2, board_size // 2, 0
    temp_list_x = []
    temp_list_o = []
    tp_list_x_2 = []
    tp_list_o_2 = []
    tp_list_d = []
    score_x = value_all(board_inner, temp_list_x, value_model_X, PIECE_BLACK, board_size)
    pos_x = (0, 0)
    score_o = value_all(board_inner, temp_list_o, value_model_O, PIECE_WHITE, board_size)
    pos_o = (0, 0)
    pos_d = (0, 0)
    score_x_2 = 0
    score_o_2 = 0
    score_diff = 0
    chess_range_x = [x for x in range(board_size) if ''.join(board_inner[x]).replace(' ', '') != '']
    chess_range_y = [y for y in range(board_size) if ''.join([list(i) for i in zip(*board_inner)][y]).replace(' ', '') != '']
    if chess_range_x and chess_range_y:
        range_x = (max(0, min(chess_range_x) - 2), min(max(chess_range_x) + 2, board_size))
        range_y = (max(0, min(chess_range_y) - 2), min(max(chess_range_y) + 2, board_size))
    else:
        range_x = (0, board_size)
        range_y = (0, board_size)
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
                score_a = value_all(board_inner, tp_list_x, value_model_X, PIECE_BLACK, board_size)
                score_c = value_all(board_inner, tp_list_c, value_model_O, PIECE_WHITE, board_size)
                if score_a > score_x_2:
                    pos_x = x, y
                    tp_list_x_2 = tp_list_x
                    score_x_2 = score_a
                board_inner[x][y] = PIECE_WHITE
                score_b = value_all(board_inner, tp_list_o, value_model_O, PIECE_WHITE, board_size)
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
        score = value_all(board_inner, temp_list_x, value_model_X, PIECE_BLACK, board_size)
        board_inner[x][y] = PIECE_EMPTY
    else:
        pos = pos_d
        x, y = pos
        board_inner[x][y] = PIECE_BLACK
        temp_list_x.clear()
        temp_list_o.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, PIECE_BLACK, board_size)
        board_inner[x][y] = PIECE_EMPTY
    return pos[0], pos[1], score

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