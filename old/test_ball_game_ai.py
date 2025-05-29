import pygame
import sys
import time
import os
from config_4 import *
# 初始化 Pygame
pygame.init()

# 设置常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 40

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)  # 用于高亮获胜棋子

# 棋型评估系统（从第一个代码中提取）
# ------------------ AI评估系统开始 ------------------


def set_chess(board_inner, x, y, chr):
    if board_inner[x][y] != ' ':
        return False
    else:
        board_inner[x][y] = chr
        return True


def check_win(board_inner):
    for list_str in board_inner:
        if ''.join(list_str).find('O' * 5) != -1:
            return 0
        elif ''.join(list_str).find('X' * 5) != -1:
            return 1
    else:
        return -1


def check_win_all(board_inner):
    board_c = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_c[x - y].append(board_inner[x][y])
    board_d = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_d[x + y].append(board_inner[x][y])
    return [check_win(board_inner), check_win([list(i) for i in zip(*board_inner)]), check_win(board_c),
            check_win(board_d)]


def value(board_inner, temp_list, value_model, chr):
    score = 0
    num = 0
    for list_str in board_inner:
        if ''.join(list_str).count(chr) < 2:
            continue
        a = 0
        for i in range(11):
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
    score = 0
    temp_list = [i[1][0][:2] for i in te_list]
    if sum([temp_list.count(i) for i in ['4_', '3p']]) >= 2:
        score += 30
    elif sum([temp_list.count(i) for i in ['3p', '3_']]) >= 2 \
            and sum([temp_list.count(i) for i in ['3p']]) > 0:
        score += 15
    return score


def value_all(board_inner, temp_list, value_model, chr):
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
    t1 = time.time()
    if board_inner == [[' '] * 15 for _ in range(15)]:
        return 7, 7, 0

    temp_list_x = []
    temp_list_o = []
    tp_list_x_2 = []
    tp_list_o_2 = []
    tp_list_d = []
    score_x = value_all(board_inner, temp_list_x, value_model_X, 'X')
    pos_x = (0, 0)
    score_o = value_all(board_inner, temp_list_o, value_model_O, 'O')
    pos_o = (0, 0)
    pos_d = (0, 0)
    score_x_2 = 0
    score_o_2 = 0
    score_diff = 0

    chess_range_x = [x for x in range(15) if ''.join(board_inner[x]).replace(' ', '') != '']
    chess_range_y = [y for y in range(15) if ''.join([list(i) for i in zip(*board_inner)][y]).replace(' ', '') != '']
    range_x = (max(0, min(chess_range_x) - 2), min(max(chess_range_x) + 2, 15))
    range_y = (max(0, min(chess_range_y) - 2), min(max(chess_range_y) + 2, 15))
    num = 0

    for x in range(*range_x):
        for y in range(*range_y):
            tp_list_x = []
            tp_list_o = []
            tp_list_c = []
            if board_inner[x][y] != ' ':
                continue
            else:
                num += 1
                board_inner[x][y] = 'X'
                score_a = value_all(board_inner, tp_list_x, value_model_X, 'X')
                score_c = value_all(board_inner, tp_list_c, value_model_O, 'O')
                if score_a > score_x_2:
                    pos_x = x, y
                    tp_list_x_2 = tp_list_x
                    score_x_2 = score_a

                board_inner[x][y] = 'O'
                score_b = value_all(board_inner, tp_list_o, value_model_O, 'O')
                if score_b > score_o_2:
                    pos_o = x, y
                    tp_list_o_2 = tp_list_o
                    score_o_2 = score_b

                board_inner[x][y] = ' '
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
        board_inner[x][y] = 'X'
        temp_list_x.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, 'X')
        board_inner[x][y] = ' '
    else:
        pos = pos_d
        x, y = pos
        board_inner[x][y] = 'X'
        temp_list_x.clear()
        temp_list_o.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, 'X')
        board_inner[x][y] = ' '

    return *pos, score


# ------------------ AI评估系统结束 ------------------


class GobangGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("五子棋人机对战")
        self.clock = pygame.time.Clock()

        # 加载背景图片
        try:
            # join方法表示路径
            background_path = os.path.join("data", "background1.jpg")
            self.background_image = pygame.image.load(background_path)
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"背景图片加载失败: {e}")
            self.background_image = None

        # 初始化字体 - 使用第一个代码的字体
        try:
            self.font_dir = 'font/'
            self.font_large = pygame.font.Font(self.font_dir + '12345.TTF', 48)
            self.font_medium = pygame.font.Font(self.font_dir + '12345.TTF', 36)
            self.font_small = pygame.font.Font(self.font_dir + '12345.TTF', 24)
        except:
            # 如果字体加载失败，使用系统字体
            self.font_large = pygame.font.SysFont("simhei", 48)
            self.font_medium = pygame.font.SysFont("simhei", 36)
            self.font_small = pygame.font.SysFont("simhei", 24)

        # 游戏状态
        self.game_state = "menu"  # menu, select_side, playing, game_over
        self.board_size = 15  # 固定为15x15棋盘
        self.board = []
        self.current_player = 1  # 1 = 黑子, 2 = 白子
        self.winner = 0
        self.winning_five = []  # 存储获胜的五子位置
        self.player_side = 1  # 玩家执棋方（1=黑，2=白）
        self.ai_thinking = False  # AI是否正在思考
        self.calculate_board_params()

        # 用于撤回/恢复功能
        self.move_history = []  # 存储所有落子历史 [(row, col, player)]
        self.undo_stack = []  # 存储被撤回的落子

        # 初始化棋盘（使用字符表示）
        self.reset_game()

    def calculate_board_params(self):
        """根据棋盘大小计算相关参数"""
        self.BOARD_WIDTH = self.board_size * CELL_SIZE
        self.BOARD_HEIGHT = self.board_size * CELL_SIZE
        self.BOARD_X = (SCREEN_WIDTH - self.BOARD_WIDTH) // 2
        self.BOARD_Y = 120

    def reset_game(self):
        """重置游戏"""
        # 使用字符表示棋盘：' '=空, 'X'=黑, 'O'=白
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.winner = 0
        self.winning_five = []  # 重置获胜的五子信息
        self.move_history = []
        self.undo_stack = []
        self.ai_thinking = False

    def draw_background(self):
        """绘制背景"""
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            # 如果没有背景图片，使用渐变背景
            for y in range(SCREEN_HEIGHT):
                color_value = int(200 + 55 * (y / SCREEN_HEIGHT))
                color = (color_value, color_value - 20, color_value - 40)
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def draw_menu(self):
        """绘制开始菜单"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_large.render("五子棋人机对战", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 游戏说明
        rules = [
            "游戏规则：",
            "1. 玩家与AI轮流下棋",
            "2. 先连成5子者获胜",
            "3. 可横、竖、斜连线",
            "",
            "按键说明：",
            "U键: 撤回",
            "D键: 恢复",
            "R键: 重新开始",
            "M键: 返回菜单",
            "",
            "点击任意位置开始游戏"
        ]

        y_offset = 200
        for rule in rules:
            if rule == "游戏规则：" or rule == "按键说明：":
                text = self.font_medium.render(rule, True, RED)
            elif rule == "":
                y_offset += 10
                continue
            else:
                text = self.font_small.render(rule, True, BLACK)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

    def draw_side_selection(self):
        """绘制执棋方选择界面"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_medium.render("选择执棋方", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 执棋方选项
        sides = ["执黑先行", "执白后行"]
        side_buttons = []

        y_offset = 250
        for i, side in enumerate(sides):
            # 绘制按钮
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset, 300, 60)
            pygame.draw.rect(self.screen, BLUE, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2, border_radius=10)

            # 绘制文字
            text = self.font_medium.render(side, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            # 保存按钮信息
            side_buttons.append((button_rect, i))
            y_offset += 120

        return side_buttons

    def draw_board(self):
        """绘制棋盘"""
        # 绘制棋盘背景
        board_rect = pygame.Rect(self.BOARD_X - 20, self.BOARD_Y - 20,
                                 self.BOARD_WIDTH + 40, self.BOARD_HEIGHT + 40)
        pygame.draw.rect(self.screen, BROWN, board_rect)

        # 绘制网格线
        for i in range(self.board_size):
            # 横线
            start_x = self.BOARD_X + 20
            end_x = self.BOARD_X + self.BOARD_WIDTH - CELL_SIZE + 20
            y = self.BOARD_Y + i * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, BLACK, (start_x, y), (end_x, y), 2)

            # 竖线
            start_y = self.BOARD_Y + 20
            end_y = self.BOARD_Y + self.BOARD_HEIGHT - CELL_SIZE + 20
            x = self.BOARD_X + i * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, BLACK, (x, start_y), (x, end_y), 2)

        # 绘制天元
        center = self.board_size // 2
        x = self.BOARD_X + center * CELL_SIZE + CELL_SIZE // 2
        y = self.BOARD_Y + center * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, BLACK, (x, y), 4)

    def draw_pieces(self):
        """绘制棋子，并高亮显示获胜的五子"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != ' ':
                    x = self.BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
                    y = self.BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

                    # 检查是否是获胜的五子之一
                    is_winning = any(pos == (row, col) for pos in self.winning_five)

                    if self.board[row][col] == 'X':  # 黑子
                        pygame.draw.circle(self.screen, BLACK, (x, y), 15)
                        pygame.draw.circle(self.screen, WHITE, (x, y), 15, 2)
                        if is_winning:
                            # 高亮显示获胜的黑子
                            pygame.draw.circle(self.screen, GOLD, (x, y), 18, 3)
                    else:  # 白子
                        pygame.draw.circle(self.screen, WHITE, (x, y), 15)
                        pygame.draw.circle(self.screen, BLACK, (x, y), 15, 2)
                        if is_winning:
                            # 高亮显示获胜的白子
                            pygame.draw.circle(self.screen, GOLD, (x, y), 18, 3)

    def draw_ui(self):
        """绘制游戏界面信息"""
        # 当前玩家提示
        if self.winner == 0:
            if self.current_player == 1:
                player_text = self.font_medium.render("当前: 黑方", True, BLACK)
            else:
                player_text = self.font_medium.render("当前: 白方", True, BLACK)
        else:
            if self.winner == 1:
                player_text = self.font_medium.render("黑方获胜！", True, RED)
            else:
                player_text = self.font_medium.render("白方获胜！", True, RED)

        self.screen.blit(player_text, (50, 10))

        # 按键提示
        restart_text = self.font_small.render("R键: 重新开始", True, GRAY)
        menu_text = self.font_small.render("M键: 返回菜单", True, GRAY)
        undo_text = self.font_small.render("U键: 撤回", True, GRAY)
        redo_text = self.font_small.render("D键: 恢复", True, GRAY)

        self.screen.blit(restart_text, (SCREEN_WIDTH - 200, 10))
        self.screen.blit(menu_text, (SCREEN_WIDTH - 200, 40))
        self.screen.blit(undo_text, (SCREEN_WIDTH - 200, 70))
        self.screen.blit(redo_text, (SCREEN_WIDTH - 200, 100))

        # 显示思考状态
        if self.ai_thinking and self.winner == 0 and self.current_player != self.player_side:
            thinking_text = self.font_small.render("AI思考中...", True, RED)
            self.screen.blit(thinking_text, (50, 50))

    def get_board_position(self, mouse_pos):
        """将鼠标位置转换为棋盘坐标"""
        x, y = mouse_pos

        # 检查是否在棋盘范围内
        if (self.BOARD_X <= x <= self.BOARD_X + self.BOARD_WIDTH and
                self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_HEIGHT):

            col = (x - self.BOARD_X) // CELL_SIZE
            row = (y - self.BOARD_Y) // CELL_SIZE

            # 确保在有效范围内
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                return row, col

        return None, None

    def place_piece(self, row, col):
        """放置棋子"""
        if self.board[row][col] == ' ' and self.winner == 0:
            # 根据当前玩家确定棋子类型
            piece = 'X' if self.current_player == 1 else 'O'
            self.board[row][col] = piece

            # 记录落子历史
            self.move_history.append((row, col, self.current_player))

            # 清空恢复栈
            self.undo_stack = []

            # 检查是否获胜
            if self.check_winner(row, col):
                self.winner = self.current_player
                # 找到获胜的五子
                self.find_winning_five(row, col)
            else:
                # 切换玩家
                self.current_player = 3 - self.current_player  # 1->2, 2->1

            return True
        return False

    def undo_move(self):
        """撤回一步棋"""
        if len(self.move_history) > 0:
            # 从历史记录中取出最后一步
            row, col, player = self.move_history.pop()

            # 保存到恢复栈
            self.undo_stack.append((row, col, player))

            # 清空棋盘位置
            self.board[row][col] = ' '

            # 重置获胜状态
            self.winner = 0
            self.winning_five = []

            # 恢复当前玩家
            self.current_player = player

            return True
        return False

    def redo_move(self):
        """恢复一步棋"""
        if len(self.undo_stack) > 0:
            # 从恢复栈中取出最后一步
            row, col, player = self.undo_stack.pop()

            # 将棋子放回棋盘
            piece = 'X' if player == 1 else 'O'
            self.board[row][col] = piece

            # 添加回历史记录
            self.move_history.append((row, col, player))

            # 检查是否获胜
            if self.check_winner(row, col):
                self.winner = player
                self.find_winning_five(row, col)

            # 设置下一个玩家
            self.current_player = 3 - player

            return True
        return False

    def check_winner(self, row, col):
        """检查是否有玩家获胜"""
        player = self.board[row][col]
        if player == ' ':
            return False

        directions = [
            (0, 1),  # 水平
            (1, 0),  # 垂直
            (1, 1),  # 主对角线
            (1, -1)  # 反对角线
        ]

        for dr, dc in directions:
            count = 1  # 包含当前棋子

            # 向一个方向检查
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                count += 1
                r += dr
                c += dc

            # 向相反方向检查
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True

        return False

    def find_winning_five(self, row, col):
        """找到获胜的五子位置"""
        player = self.board[row][col]
        directions = [
            (0, 1),  # 水平
            (1, 0),  # 垂直
            (1, 1),  # 主对角线
            (1, -1)  # 反对角线
        ]

        self.winning_five = []  # 清空之前的获胜五子

        for dr, dc in directions:
            # 存储当前方向上的连续棋子
            line_pieces = [(row, col)]

            # 向一个方向检查
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                line_pieces.append((r, c))
                r += dr
                c += dc

            # 向相反方向检查
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                line_pieces.append((r, c))
                r -= dr
                c -= dc

            # 如果找到至少5个连续棋子
            if len(line_pieces) >= 5:
                # 按方向排序，确保是连续的
                if dr != 0 or dc != 0:
                    line_pieces.sort(key=lambda pos: (pos[0] * dr + pos[1] * dc,
                                                      (pos[1] * dc if dr == 0 else pos[0] * dr)))

                # 找到包含当前棋子的最长连续段
                start_index = None
                for i, (r, c) in enumerate(line_pieces):
                    if r == row and c == col:
                        start_index = i
                        break

                if start_index is not None:
                    # 获取连续的5个子
                    start = max(0, start_index - 4)
                    end = min(len(line_pieces), start_index + 5)
                    self.winning_five = line_pieces[start:end]

                    # 确保我们有连续的5个
                    if len(self.winning_five) > 5:
                        # 找到包含当前棋子的连续5子
                        for i in range(len(self.winning_five) - 4):
                            if any(pos == (row, col) for pos in self.winning_five[i:i + 5]):
                                self.winning_five = self.winning_five[i:i + 5]
                                return
                    elif len(self.winning_five) == 5:
                        return

    def ai_move(self):
        """AI进行移动"""
        if self.winner != 0:
            return

        self.ai_thinking = True
        pygame.display.flip()  # 更新显示，显示"AI思考中..."

        # 调用AI函数计算落子位置
        try:
            row, col, _ = value_chess(self.board)
            self.place_piece(row, col)
        except Exception as e:
            print(f"AI移动出错: {e}")

        self.ai_thinking = False

    def handle_menu_events(self, event):
        """处理菜单事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.game_state = "select_side"

    def handle_side_selection_events(self, event):
        """处理执棋方选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            side_buttons = self.draw_side_selection()

            for button, side_idx in side_buttons:
                if button.collidepoint(mouse_pos):
                    # 设置玩家执棋方
                    self.player_side = 1 if side_idx == 0 else 2

                    # 重置游戏
                    self.reset_game()
                    self.game_state = "playing"
                    return

    def handle_game_events(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 只有在玩家回合才能下棋
                if self.current_player == self.player_side and not self.ai_thinking:
                    row, col = self.get_board_position(event.pos)
                    if row is not None and col is not None:
                        self.place_piece(row, col)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R键重新开始
                self.reset_game()
            elif event.key == pygame.K_m:  # M键返回菜单
                self.game_state = "menu"
            elif event.key == pygame.K_u:  # U键撤回
                self.undo_move()
            elif event.key == pygame.K_d:  # D键恢复
                self.redo_move()

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif self.game_state == "menu":
                    self.handle_menu_events(event)

                elif self.game_state == "select_side":
                    self.handle_side_selection_events(event)

                elif self.game_state == "playing":
                    self.handle_game_events(event)

            # 绘制
            if self.game_state == "menu":
                self.draw_menu()

            elif self.game_state == "select_side":
                self.draw_side_selection()

            elif self.game_state == "playing":
                self.draw_background()
                self.draw_board()
                self.draw_pieces()
                self.draw_ui()

                # 如果是AI回合且没有获胜，调用AI移动
                if (self.current_player != self.player_side and
                        self.winner == 0 and
                        not self.ai_thinking):
                    self.ai_move()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = GobangGame()
    game.run()


if __name__ == "__main__":
    main()
