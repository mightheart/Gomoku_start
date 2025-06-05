import pygame
import sys
import numpy as np
import torch
import os
import time
from config_4 import *
# 初始化 Pygame
pygame.init()

# 设置常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900  # 增加高度以容纳更多UI元素
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
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)



class GomokuNet(torch.nn.Module):
    """神经网络模型，支持不同棋盘大小"""

    def __init__(self, board_size=15):
        super(GomokuNet, self).__init__()
        self.board_size = board_size
        self.action_size = board_size * board_size

        self.conv1 = torch.nn.Conv2d(4, 64, kernel_size=3, padding=1)
        self.conv2 = torch.nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv3 = torch.nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv4 = torch.nn.Conv2d(64, 64, kernel_size=3, padding=1)

        # 策略头
        self.policy_conv = torch.nn.Conv2d(64, 2, kernel_size=1)
        self.policy_fc = torch.nn.Linear(2 * board_size * board_size, self.action_size)

        # 价值头
        self.value_conv = torch.nn.Conv2d(64, 1, kernel_size=1)
        self.value_fc1 = torch.nn.Linear(board_size * board_size, 64)
        self.value_fc2 = torch.nn.Linear(64, 1)

    def forward(self, x):
        # 输入形状: (batch, 4, board_size, board_size)
        x = torch.nn.functional.relu(self.conv1(x))
        x = torch.nn.functional.relu(self.conv2(x))
        x = torch.nn.functional.relu(self.conv3(x))
        x = torch.nn.functional.relu(self.conv4(x))

        # 策略头
        policy = self.policy_conv(x)
        policy = policy.view(policy.size(0), -1)
        policy = self.policy_fc(policy)

        # 价值头
        value = torch.nn.functional.relu(self.value_conv(x))
        value = value.view(value.size(0), -1)
        value = torch.nn.functional.relu(self.value_fc1(value))
        value = torch.tanh(self.value_fc2(value))

        return policy, value


class StaticEvaluator:
    """静态棋型评估器，支持不同棋盘大小"""

    def __init__(self, board_size, value_model_X, value_model_O):
        self.board_size = board_size
        self.value_model_X = value_model_X
        self.value_model_O = value_model_O
        self.pattern_cache = {}

    def get_static_scores(self, board, current_player):
        """获取所有合法动作的静态评估分数"""
        scores = {}
        action_size = self.board_size * self.board_size

        for action in range(action_size):
            r, c = action // self.board_size, action % self.board_size
            if board[r, c] != 0:  # 已有棋子，跳过
                continue

            # 模拟落子
            new_board = board.copy()
            new_board[r, c] = current_player

            # 计算分数
            score = self.evaluate_board(new_board, current_player)
            scores[action] = score

        return scores

    def evaluate_board(self, board, player):
        """评估整个棋盘的分数"""
        score = 0
        model = self.value_model_X if player == 1 else self.value_model_O

        # 检查所有可能的棋型
        for r in range(self.board_size):
            for c in range(self.board_size):
                # 检查四个方向：水平、垂直、对角线、反对角线
                for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    # 获取该方向的字符串表示
                    pattern_str = self.get_direction_pattern(board, r, c, direction, 5, player)

                    # 在棋型字典中查找匹配
                    if pattern_str in self.pattern_cache:
                        score += self.pattern_cache[pattern_str]
                        continue

                    # 遍历所有棋型进行匹配
                    for count, patterns in model.items():
                        for pattern_id, (pattern, value) in patterns.items():
                            if pattern_str.startswith(pattern) or pattern_str.endswith(pattern):
                                self.pattern_cache[pattern_str] = value
                                score += value
                                break

        return score

    def get_direction_pattern(self, board, r, c, direction, length, player):
        """获取特定方向的棋子模式字符串"""
        dr, dc = direction
        pattern = []

        # 获取该方向上的棋子序列
        for i in range(-length + 1, length):
            nr, nc = r + i * dr, c + i * dc
            if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                if board[nr, nc] == player:
                    pattern.append('X')
                elif board[nr, nc] == -player:
                    pattern.append('O')
                else:
                    pattern.append(' ')
            else:  # 超出边界
                pattern.append('O')  # 边界视为对手棋子

        return ''.join(pattern)


class MCTS:
    """蒙特卡洛树搜索，支持不同棋盘大小"""

    def __init__(self, model, static_evaluator, c_puct=1.0, num_simulations=200, static_weight=0.1):
        self.model = model
        self.static_evaluator = static_evaluator
        self.c_puct = c_puct
        self.num_simulations = num_simulations
        self.static_weight = static_weight
        self.root = Node()
        self.board_size = model.board_size
        self.action_size = self.board_size * self.board_size

    def run(self, state, game, temperature=1.0):
        """执行MCTS搜索"""
        # 获取静态评估分数
        static_scores = self.static_evaluator.get_static_scores(
            game.board, game.current_player
        )

        # 扩展根节点
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        action_probs, _ = self.model(state_tensor)
        action_probs = torch.nn.functional.softmax(action_probs, dim=1).squeeze(0).detach().numpy()

        # 只保留合法动作
        valid_moves = game.get_valid_moves()
        mask = np.ones(self.action_size, dtype=bool)
        mask[valid_moves] = False
        action_probs[mask] = 0
        if np.sum(action_probs) > 0:
            action_probs /= np.sum(action_probs)

        # 扩展根节点
        self.root.expand(list(enumerate(action_probs)), state, static_scores)

        # 执行模拟
        for _ in range(self.num_simulations):
            node = self.root
            search_path = [node]

            # 选择阶段
            while node.expanded():
                action, node = node.select_child(self.c_puct, self.static_weight)
                search_path.append(node)

            # 获取游戏状态
            parent = search_path[-2]
            game_state = parent.state

            # 检查游戏是否结束
            game_copy = GomokuGame(self.board_size)
            game_copy.board = np.copy(game.board)
            game_copy.current_player = game.current_player

            # 回溯应用动作
            for i in range(1, len(search_path) - 1):
                action = list(parent.children.keys())[list(parent.children.values()).index(search_path[i])]
                game_copy.make_move(action)
                parent = search_path[i]

            # 扩展和模拟
            if not game_copy.done:
                # 获取策略和价值
                state_tensor = torch.tensor(game_copy.get_state(), dtype=torch.float32).unsqueeze(0)
                action_probs, value = self.model(state_tensor)
                action_probs = torch.nn.functional.softmax(action_probs, dim=1).squeeze(0).detach().numpy()

                # 获取静态评估分数
                static_scores = self.static_evaluator.get_static_scores(
                    game_copy.board, game_copy.current_player
                )

                # 只保留合法动作
                valid_moves = game_copy.get_valid_moves()
                mask = np.ones(self.action_size, dtype=bool)
                mask[valid_moves] = False
                action_probs[mask] = 0
                if np.sum(action_probs) > 0:
                    action_probs /= np.sum(action_probs)

                # 扩展节点
                node.expand(list(enumerate(action_probs)), game_copy.get_state(), static_scores)
            else:
                value = 1.0 if game_copy.winner == game.current_player else -1.0

            # 回溯更新
            self.backpropagate(search_path, value, game.current_player)

        # 获取访问计数
        visit_counts = np.zeros(self.action_size)
        for action, child in self.root.children.items():
            visit_counts[action] = child.visit_count

        # 应用温度参数
        visit_counts = visit_counts ** (1.0 / temperature)
        if np.sum(visit_counts) > 0:
            visit_counts /= np.sum(visit_counts)

        return visit_counts

    def backpropagate(self, search_path, value, current_player):
        """回溯更新节点值"""
        for node in reversed(search_path):
            node.value_sum += value if node == search_path[0] else -value
            node.visit_count += 1

    def get_action(self, state, game, temperature=1.0):
        """根据MCTS结果选择动作"""
        action_probs = self.run(state, game, temperature)
        return np.random.choice(self.action_size, p=action_probs)

    def update_root(self, action):
        """更新根节点为选择的子节点"""
        if action in self.root.children:
            self.root = self.root.children[action]
            self.root.parent = None
        else:
            self.root = Node()


class Node:
    """MCTS节点类"""

    def __init__(self, parent=None, prior_prob=0.0):
        self.parent = parent
        self.children = {}  # action: Node
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior_prob
        self.state = None
        self.reward = 0.0  # 静态评估分数

    def expanded(self):
        return len(self.children) > 0

    def value(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def get_ucb_score(self, c_puct=1.0, static_weight=0.1):
        """计算UCB分数，融合静态评估分数"""
        if self.visit_count == 0:
            q_value = 0.0
        else:
            q_value = self.value()

        # 融合静态评估分数（随着访问次数增加而权重降低）
        decay_factor = 1.0 / (1.0 + self.visit_count)
        static_component = self.reward * static_weight * decay_factor

        # 计算UCB分数
        ucb = q_value + c_puct * self.prior * np.sqrt(self.parent.visit_count) / (1 + self.visit_count)

        return ucb + static_component

    def select_child(self, c_puct=1.0, static_weight=0.1):
        """选择UCB分数最高的子节点"""
        return max(self.children.items(),
                   key=lambda item: item[1].get_ucb_score(c_puct, static_weight))

    def expand(self, action_probs, state, static_scores=None):
        """扩展节点"""
        for action, prob in action_probs:
            if action not in self.children:
                # 获取静态评估分数（如果有）
                reward = static_scores[action] if static_scores and action in static_scores else 0.0
                self.children[action] = Node(parent=self, prior_prob=prob)
                self.children[action].reward = reward
        self.state = state


class GomokuGame:
    """五子棋游戏环境，支持不同棋盘大小"""

    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = 1  # 1: 玩家1 (X), -1: 玩家2 (O)
        self.last_move = None
        self.winner = 0
        self.done = False
        self.action_size = board_size * board_size

    def reset(self):
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        self.last_move = None
        self.winner = 0
        self.done = False
        return self.get_state()

    def get_state(self):
        """获取当前状态表示"""
        state = np.zeros((4, self.board_size, self.board_size), dtype=float)

        # 通道0: 当前玩家的棋子位置
        # 通道1: 对手的棋子位置
        # 通道2: 空位
        # 通道3: 最近一步的位置

        player_pieces = (self.board == self.current_player).astype(float)
        opponent_pieces = (self.board == -self.current_player).astype(float)
        empty = (self.board == 0).astype(float)

        state[0] = player_pieces
        state[1] = opponent_pieces
        state[2] = empty

        if self.last_move:
            r, c = self.last_move
            state[3, r, c] = 1.0

        return state

    def is_valid_move(self, action):
        r, c = action // self.board_size, action % self.board_size
        return self.board[r, c] == 0

    def make_move(self, action):
        r, c = action // self.board_size, action % self.board_size
        if self.board[r, c] != 0:
            return False

        self.board[r, c] = self.current_player
        self.last_move = (r, c)

        # 检查是否获胜
        if self.check_win(r, c):
            self.winner = self.current_player
            self.done = True
        # 检查是否平局
        elif np.count_nonzero(self.board == 0) == 0:
            self.done = True

        self.current_player = -self.current_player
        return True

    def check_win(self, r, c):
        player = self.board[r, c]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平, 垂直, 对角线, 反对角线

        for dr, dc in directions:
            count = 1  # 当前位置已经有一个棋子

            # 正向检查
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.board_size and 0 <= nc < self.board_size and self.board[nr, nc] == player:
                count += 1
                nr += dr
                nc += dc

            # 反向检查
            nr, nc = r - dr, c - dc
            while 0 <= nr < self.board_size and 0 <= nc < self.board_size and self.board[nr, nc] == player:
                count += 1
                nr -= dr
                nc -= dc

            if count >= 5:
                return True

        return False

    def get_valid_moves(self):
        return [i for i in range(self.action_size) if self.is_valid_move(i)]


class GobangGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("五子棋游戏")
        self.clock = pygame.time.Clock()

        # 加载背景图片
        try:
            self.background_image = pygame.image.load("background.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background_image = None

        # 初始化字体
        try:
            self.font_large = pygame.font.SysFont("simhei", 48)
            self.font_medium = pygame.font.SysFont("simhei", 36)
            self.font_small = pygame.font.SysFont("simhei", 24)
        except:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)

        # 游戏状态
        self.game_state = "menu"  # menu, select_size, select_ai, playing, game_over
        self.board_size = 15  # 默认棋盘大小
        self.board = []
        self.current_player = 1  # 1 = 黑子, 2 = 白子
        self.winner = 0
        self.winning_five = []  # 存储获胜的五子位置
        self.ai_player = 0  # 0: 无AI, 1: AI黑棋, 2: AI白棋
        self.ai_thinking = False
        self.ai_move = None
        self.ai_models = {}  # 存储不同棋盘大小的AI模型
        self.ai_game = None  # AI使用的游戏环境
        self.ai_mcts = None  # AI使用的MCTS
        self.calculate_board_params()
        self.load_ai_models()

    def load_ai_models(self):
        """加载不同棋盘大小的AI模型"""
        self.ai_models = {}
        model_dir = "models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
            return

        for size in [11, 13, 15]:
            model_path = os.path.join(model_dir, f"gomoku_{size}x{size}.pth")
            if os.path.exists(model_path):
                try:
                    model = GomokuNet(board_size=size)
                    model.load_state_dict(torch.load(model_path))
                    model.eval()
                    static_evaluator = StaticEvaluator(size, value_model_X_test, value_model_O_test)
                    self.ai_models[size] = (model, static_evaluator)
                    print(f"Loaded model for {size}x{size} board")
                except Exception as e:
                    print(f"Error loading model for {size}x{size}: {str(e)}")

    def calculate_board_params(self):
        """根据棋盘大小计算相关参数"""
        self.BOARD_WIDTH = self.board_size * CELL_SIZE
        self.BOARD_HEIGHT = self.board_size * CELL_SIZE
        self.BOARD_X = (SCREEN_WIDTH - self.BOARD_WIDTH) // 2
        self.BOARD_Y = 120

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

    def reset_game(self):
        """重置游戏"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.winner = 0
        self.winning_five = []  # 重置获胜的五子信息
        self.ai_thinking = False
        self.ai_move = None

        # 初始化AI游戏环境
        self.ai_game = GomokuGame(self.board_size)

        # 如果存在对应大小的AI模型，初始化MCTS
        if self.board_size in self.ai_models:
            model, static_evaluator = self.ai_models[self.board_size]
            self.ai_mcts = MCTS(model, static_evaluator, num_simulations=200, static_weight=0.0)
            self.ai_mcts.root = Node()
        else:
            self.ai_mcts = None
            print(f"No AI model for {self.board_size}x{self.board_size} board")

    def draw_menu(self):
        """绘制开始菜单"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_large.render("五子棋游戏", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 游戏说明
        rules = [
            "游戏规则：",
            "1. 黑白双方轮流下棋",
            "2. 先连成5子者获胜",
            "3. 可横、竖、斜连线",
            "",
            "点击任意位置开始游戏"
        ]

        y_offset = 250
        for rule in rules:
            if rule == "游戏规则：":
                text = self.font_medium.render(rule, True, RED)
            elif rule == "":
                y_offset += 10
                continue
            else:
                text = self.font_small.render(rule, True, BLACK)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40

    def draw_size_selection(self):
        """绘制棋盘大小选择界面"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_medium.render("选择棋盘大小", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        # 棋盘大小选项
        sizes = ["15×15 (标准)", "13×13", "11×11"]
        size_buttons = []

        y_offset = 200
        for i, size in enumerate(sizes):
            # 绘制按钮
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset, 300, 60)
            pygame.draw.rect(self.screen, BLUE, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2, border_radius=10)

            # 绘制文字
            text = self.font_medium.render(size, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            # 保存按钮信息
            size_buttons.append((button_rect, i))
            y_offset += 100

        return size_buttons

    def draw_ai_selection(self):
        """绘制AI选择界面"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_medium.render("选择对战模式", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        # AI选项
        ai_options = [
            "玩家对玩家 (PVP)",
            "玩家执黑 (AI执白)",
            "玩家执白 (AI执黑)",
            "AI对AI (观看)"
        ]
        ai_buttons = []

        y_offset = 200
        for i, option in enumerate(ai_options):
            # 绘制按钮
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, y_offset, 400, 60)
            color = GREEN if i == 0 else BLUE
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2, border_radius=10)

            # 绘制文字
            text = self.font_medium.render(option, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            # 保存按钮信息
            ai_buttons.append((button_rect, i))
            y_offset += 100

        return ai_buttons

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
                if self.board[row][col] != 0:
                    x = self.BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
                    y = self.BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

                    # 检查是否是获胜的五子之一
                    is_winning = any(pos == (row, col) for pos in self.winning_five)

                    if self.board[row][col] == 1:  # 黑子
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

        # 重新开始按钮
        restart_text = self.font_small.render("按R键重新开始", True, GRAY)
        self.screen.blit(restart_text, (SCREEN_WIDTH - 200, 10))

        # 返回菜单按钮
        menu_text = self.font_small.render("按M键返回菜单", True, GRAY)
        self.screen.blit(menu_text, (SCREEN_WIDTH - 200, 40))

        # 显示AI状态
        if self.ai_player > 0:
            ai_status = "AI思考中..." if self.ai_thinking else "AI已就绪"
            ai_text = self.font_small.render(ai_status, True, DARK_BLUE)
            self.screen.blit(ai_text, (50, 50))

            # 显示AI模型状态
            model_status = f"AI模型: {self.board_size}x{self.board_size}"
            if self.board_size in self.ai_models:
                model_status += " (已加载)"
                color = GREEN
            else:
                model_status += " (未找到)"
                color = RED

            model_text = self.font_small.render(model_status, True, color)
            self.screen.blit(model_text, (50, 80))

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
        if self.board[row][col] == 0 and self.winner == 0:
            self.board[row][col] = self.current_player

            # 更新AI游戏环境
            if self.ai_game:
                action = row * self.board_size + col
                self.ai_game.make_move(action)
                if self.ai_mcts:
                    self.ai_mcts.update_root(action)

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

    def check_winner(self, row, col):
        """检查是否有玩家获胜"""
        player = self.board[row][col]
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

    def handle_menu_events(self, event):
        """处理菜单事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.game_state = "select_size"

    def handle_size_selection_events(self, event):
        """处理棋盘大小选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            size_buttons = self.draw_size_selection()

            for button, size_idx in size_buttons:
                if button.collidepoint(mouse_pos):
                    # 设置棋盘大小
                    if size_idx == 0:
                        self.board_size = 15
                    elif size_idx == 1:
                        self.board_size = 13
                    else:  # size_idx == 2
                        self.board_size = 11

                    # 进入AI选择界面
                    self.game_state = "select_ai"
                    return

    def handle_ai_selection_events(self, event):
        """处理AI选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            ai_buttons = self.draw_ai_selection()

            for button, ai_idx in ai_buttons:
                if button.collidepoint(mouse_pos):
                    # 设置AI模式
                    self.ai_player = ai_idx

                    # 重新计算棋盘参数并重置游戏
                    self.calculate_board_params()
                    self.reset_game()
                    self.game_state = "playing"
                    return

    def handle_game_events(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                # 如果是AI回合，不处理玩家点击
                if self.ai_player == 1 and self.current_player == 1:  # AI执黑
                    return
                if self.ai_player == 2 and self.current_player == 2:  # AI执白
                    return

                row, col = self.get_board_position(event.pos)
                if row is not None and col is not None:
                    self.place_piece(row, col)

                    # 如果是AI对战模式，且游戏未结束，触发AI思考
                    if self.ai_player > 0 and self.winner == 0:
                        self.ai_thinking = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R键重新开始
                self.reset_game()
            elif event.key == pygame.K_m:  # M键返回菜单
                self.game_state = "menu"

    def ai_think(self):
        """AI思考并落子"""
        if not self.ai_thinking or not self.ai_mcts or not self.ai_game:
            return

        # 确保是AI的回合
        if (self.ai_player == 1 and self.current_player != 1) or \
                (self.ai_player == 2 and self.current_player != 2):
            return

        # 获取当前状态
        state = self.ai_game.get_state()

        # AI思考并获取动作
        action = self.ai_mcts.get_action(state, self.ai_game, temperature=0.1)

        # 将动作转换为棋盘坐标
        row = action // self.board_size
        col = action % self.board_size

        # 在棋盘上落子
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player

            # 更新AI游戏环境
            self.ai_game.make_move(action)
            self.ai_mcts.update_root(action)

            # 检查是否获胜
            if self.check_winner(row, col):
                self.winner = self.current_player
                self.find_winning_five(row, col)
            else:
                # 切换玩家
                self.current_player = 3 - self.current_player

            # 如果不是AI对战AI模式，结束思考
            if self.ai_player != 3:
                self.ai_thinking = False

            # 如果是AI对战AI模式，继续思考
            elif self.ai_player == 3 and self.winner == 0:
                # 延迟一下，让玩家能看到每一步
                pygame.time.delay(500)
                self.ai_thinking = True

    def run(self):
        """运行游戏主循环"""
        running = True
        last_ai_think_time = 0
        ai_think_delay = 100  # AI思考最小间隔(毫秒)

        while running:
            current_time = pygame.time.get_ticks()

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif self.game_state == "menu":
                    self.handle_menu_events(event)

                elif self.game_state == "select_size":
                    self.handle_size_selection_events(event)

                elif self.game_state == "select_ai":
                    self.handle_ai_selection_events(event)

                elif self.game_state == "playing":
                    self.handle_game_events(event)

            # AI思考
            if self.ai_thinking and current_time - last_ai_think_time > ai_think_delay:
                self.ai_think()
                last_ai_think_time = current_time

            # 绘制
            if self.game_state == "menu":
                self.draw_menu()

            elif self.game_state == "select_size":
                self.draw_size_selection()

            elif self.game_state == "select_ai":
                self.draw_ai_selection()

            elif self.game_state == "playing":
                self.draw_background()
                self.draw_board()
                self.draw_pieces()
                self.draw_ui()

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