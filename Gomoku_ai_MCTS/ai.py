""" 
AI相关功能 - MCTS版本
"""
import math
import copy
import time
import random
from utils.constants import *
from utils.chessboard import ChessBoard
from utils.gomoku_ai import GomokuAI

class MCTSNode:
    """MCTS节点"""
    def __init__(self, board, player, move=None, parent=None):
        self.board = copy.deepcopy(board)
        self.player = player  # 当前轮到谁下棋
        self.move = move  # 到达此节点的移动
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = self.get_legal_moves()
        
    def get_legal_moves(self):
        """获取合法移动位置"""
        moves = []
        # 只在已有棋子周围2格范围内搜索
        candidates = set()
        
        # 如果棋盘为空，返回中心位置
        if all(self.board[i][j] == 0 for i in range(15) for j in range(15)):
            return [(7, 7)]
        
        for i in range(15):
            for j in range(15):
                if self.board[i][j] != 0:
                    for di in range(-2, 3):
                        for dj in range(-2, 3):
                            ni, nj = i + di, j + dj
                            if (0 <= ni < 15 and 0 <= nj < 15 and 
                                self.board[ni][nj] == 0):
                                candidates.add((ni, nj))
        
        return list(candidates)
    
    def is_terminal(self):
        """检查是否为终端节点"""
        return self.check_winner() is not None or len(self.get_legal_moves()) == 0
    
    def check_winner(self):
        """检查是否有获胜者"""
        for i in range(15):
            for j in range(15):
                if self.board[i][j] != 0:
                    if self.check_five_in_row(i, j, self.board[i][j]):
                        return self.board[i][j]
        return None
    
    def check_five_in_row(self, row, col, player):
        """检查五连"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            # 正方向
            i, j = row + dx, col + dy
            while 0 <= i < 15 and 0 <= j < 15 and self.board[i][j] == player:
                count += 1
                i, j = i + dx, j + dy
            # 负方向
            i, j = row - dx, col - dy
            while 0 <= i < 15 and 0 <= j < 15 and self.board[i][j] == player:
                count += 1
                i, j = i - dx, j - dy
            if count >= 5:
                return True
        return False
    
    def add_child(self, move):
        """添加子节点"""
        new_board = copy.deepcopy(self.board)
        new_board[move[0]][move[1]] = self.player
        child = MCTSNode(new_board, 3 - self.player, move, self)
        self.children.append(child)
        return child
    
    def update(self, result):
        """更新节点统计信息"""
        self.visits += 1
        self.wins += result
    
    def ucb1_value(self, c=1.4):
        """计算UCB1值"""
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration


class MCTSAIEngine:
    """MCTS AI核心引擎"""
    
    def __init__(self, iterations=1000, max_time=5.0, c_param=1.4):
        self.iterations = iterations
        self.max_time = max_time
        self.c_param = c_param
        self.board_size = 15
        self.boardMap = None
        self.currentI = 0
        self.currentJ = 0
    
    def get_next_move(self, board, player):
        """
        获取下一步移动
        board: 15x15的二维数组，0表示空位，1和-1表示不同玩家
        player: 当前玩家标识 (1 或 -1)
        返回: (row, col)
        """
        start_time = time.time()
        
        # 转换棋盘格式
        converted_board = self.convert_board_format(board)
        
        # 创建根节点
        mcts_player = 1 if player == 1 else 2
        root = MCTSNode(converted_board, mcts_player)
        
        # 如果没有合法移动
        if not root.get_legal_moves():
            return (7, 7)
        
        # 第一步下中心
        if len(root.get_legal_moves()) == 1 and root.get_legal_moves()[0] == (7, 7):
            self.currentI, self.currentJ = 7, 7
            return (7, 7)
        
        # MCTS主循环
        iteration = 0
        while iteration < self.iterations and time.time() - start_time < self.max_time:
            # 1. 选择
            node = self.select(root)
            
            # 2. 扩展
            if not node.is_terminal() and node.untried_moves:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)
                node = node.add_child(move)
            
            # 3. 模拟
            result = self.simulate(node, mcts_player)
            
            # 4. 反向传播
            self.backpropagate(node, result)
            
            iteration += 1
        
        # 选择最佳移动
        if not root.children:
            self.currentI, self.currentJ = 7, 7
            return (7, 7)
        
        best_child = max(root.children, key=lambda c: c.visits)
        self.currentI, self.currentJ = best_child.move
        
        print(f"MCTS完成 {iteration} 次迭代，选择位置 ({self.currentI}, {self.currentJ})")
        print(f"最佳移动访问次数: {best_child.visits}, 胜率: {best_child.wins/best_child.visits:.3f}")
        
        return (self.currentI, self.currentJ)
    
    def convert_board_format(self, board):
        """转换棋盘格式：从 1/-1 格式转换为 1/2 格式"""
        converted = []
        for row in board:
            converted_row = []
            for cell in row:
                if cell == 0:
                    converted_row.append(0)
                elif cell == 1:
                    converted_row.append(1)
                elif cell == -1:
                    converted_row.append(2)
            converted.append(converted_row)
        return converted
    
    def select(self, node):
        """选择阶段：使用UCB1选择最佳子节点"""
        while not node.is_terminal():
            if node.untried_moves:
                return node
            else:
                node = max(node.children, key=lambda c: c.ucb1_value(self.c_param))
        return node
    
    def simulate(self, node, ai_player):
        """模拟阶段：随机对局直到游戏结束"""
        current_board = copy.deepcopy(node.board)
        current_player = node.player
        
        # 检查当前节点是否已经有获胜者
        winner = node.check_winner()
        if winner:
            return 1 if winner == ai_player else 0
        
        # 随机模拟游戏
        max_moves = 50  # 限制模拟长度
        moves_count = 0
        
        while moves_count < max_moves:
            # 获取合法移动
            legal_moves = self.get_simulation_moves(current_board)
            if not legal_moves:
                break
            
            # 使用启发式策略选择移动
            move = self.choose_simulation_move(current_board, legal_moves, current_player)
            
            # 执行移动
            current_board[move[0]][move[1]] = current_player
            
            # 检查是否获胜
            if self.check_winner_fast(current_board, move, current_player):
                return 1 if current_player == ai_player else 0
            
            # 切换玩家
            current_player = 3 - current_player
            moves_count += 1
        
        # 如果没有明确胜负，使用简单评估
        return self.evaluate_simulation_result(current_board, ai_player)
    
    def get_simulation_moves(self, board):
        """获取模拟中的候选移动"""
        moves = []
        for i in range(15):
            for j in range(15):
                if board[i][j] != 0:
                    # 在已有棋子周围寻找空位
                    for di in range(-1, 2):
                        for dj in range(-1, 2):
                            ni, nj = i + di, j + dj
                            if (0 <= ni < 15 and 0 <= nj < 15 and 
                                board[ni][nj] == 0 and (ni, nj) not in moves):
                                moves.append((ni, nj))
        
        return moves if moves else [(7, 7)] if board[7][7] == 0 else []
    
    def choose_simulation_move(self, board, moves, player):
        """在模拟中选择移动（带有轻量级启发）"""
        # 检查是否有立即获胜的移动
        for move in moves:
            board[move[0]][move[1]] = player
            if self.check_winner_fast(board, move, player):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 0
        
        # 检查是否需要阻止对手获胜
        opponent = 3 - player
        for move in moves:
            board[move[0]][move[1]] = opponent
            if self.check_winner_fast(board, move, opponent):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 0
        
        # 否则随机选择
        return random.choice(moves)
    
    def check_winner_fast(self, board, last_move, player):
        """快速检查最后一步是否导致获胜"""
        row, col = last_move
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            # 正方向
            i, j = row + dx, col + dy
            while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
                count += 1
                i, j = i + dx, j + dy
            # 负方向
            i, j = row - dx, col - dy
            while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
                count += 1
                i, j = i - dx, j - dy
            
            if count >= 5:
                return True
        return False
    
    def evaluate_simulation_result(self, board, ai_player):
        """评估模拟结果（当没有明确胜负时）"""
        # 简单的位置评估：更倾向于中心位置
        ai_score = 0
        opponent_score = 0
        opponent = 3 - ai_player
        
        for i in range(15):
            for j in range(15):
                if board[i][j] == ai_player:
                    ai_score += self.position_value(i, j)
                elif board[i][j] == opponent:
                    opponent_score += self.position_value(i, j)
        
        if ai_score > opponent_score:
            return 0.6  # 轻微优势
        elif ai_score < opponent_score:
            return 0.4  # 轻微劣势
        else:
            return 0.5  # 平局
    
    def position_value(self, row, col):
        """位置价值评估"""
        center_distance = abs(row - 7) + abs(col - 7)
        return max(0, 14 - center_distance)
    
    def backpropagate(self, node, result):
        """反向传播更新"""
        while node is not None:
            node.update(result)
            # 对于对手节点，结果需要反转
            if hasattr(node.parent, 'player') and node.parent and node.parent.player != node.player:
                result = 1 - result
            node = node.parent


class MCTSAIPlayer(GomokuAI):
    """基于MCTS算法的AI玩家"""
    
    def __init__(self, iterations=1000, max_time=3.0, c_param=1.4):
        self.thinking = False
        self.iterations = iterations
        self.max_time = max_time
        self.engine = MCTSAIEngine(iterations, max_time, c_param)
    
    def convert_board(self, board, player_side):
        """将框架棋盘转换为MCTS引擎的内部表示"""
        converted = []
        for row in board:
            converted_row = []
            for cell in row:
                if cell == PIECE_EMPTY:
                    converted_row.append(0)
                elif cell == PIECE_BLACK:
                    # 根据AI角色决定表示
                    converted_row.append(1 if player_side == PLAYER_BLACK else -1)
                elif cell == PIECE_WHITE:
                    converted_row.append(-1 if player_side == PLAYER_BLACK else 1)
            converted.append(converted_row)
        return converted
    
    def get_next_chessboard(self, chessboard: ChessBoard, player_side: int) -> ChessBoard:
        """获取AI的下一步棋盘状态"""
        if chessboard.winner != 0:
            return chessboard
        
        board_size = chessboard.size
        board_inner = chessboard.board
        
        # AI计算下一步
        row, col = self.get_move(board_inner, board_size, player_side)
        
        # 根据player_side确定棋子类型
        piece_type = PIECE_BLACK if player_side == PLAYER_BLACK else PIECE_WHITE
        
        # 更新棋盘状态
        if 0 <= row < board_size and 0 <= col < board_size and board_inner[row][col] == PIECE_EMPTY:
            chessboard.place_stone(row, col, player_side)
        
        return chessboard
    
    def get_move(self, board, board_size, player_side):
        """获取AI的下一步移动"""
        self.thinking = True
        try:
            # 转换棋盘表示
            converted_board = self.convert_board(board, player_side)
            
            # 初始化引擎
            self.engine = MCTSAIEngine(self.iterations, self.max_time)
            self.engine.board_size = board_size
            
            # 如果是空棋盘，直接返回中心点
            if all(cell == 0 for row in converted_board for cell in row):
                center = board_size // 2
                return center, center
            
            # 确定玩家标识 (1 for AI, -1 for opponent)
            player = 1 if player_side == PLAYER_BLACK else -1
            
            # 执行MCTS搜索
            row, col = self.engine.get_next_move(converted_board, player)
            
            print(f"MCTS AI计算结果: ({row}, {col})")
            return row, col
        except Exception as e:
            print(f"MCTS AI计算出错: {e}")
            return self._get_fallback_move(board, board_size)
        finally:
            self.thinking = False
    
    def _get_fallback_move(self, board, board_size):
        """备用策略：在棋盘上寻找空位置"""
        center = board_size // 2
        for radius in range(board_size // 2 + 1):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r, c = center + dr, center + dc
                    if (0 <= r < board_size and 0 <= c < board_size and 
                        board[r][c] == PIECE_EMPTY):
                        return r, c
        return 0, 0