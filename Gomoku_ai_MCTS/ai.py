import copy
import time
import random
import math

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


class GomokuMCTS:
    def __init__(self, player=2, opponent=1, iterations=1000, max_time=5.0):
        """
        五子棋MCTS AI算法
        player: AI棋子标识 (默认2)
        opponent: 对手棋子标识 (默认1)
        iterations: 最大模拟次数
        max_time: 最大思考时间(秒)
        """
        self.player = player
        self.opponent = opponent
        self.iterations = iterations
        self.max_time = max_time
    
    def get_next_move(self, board):
        """
        输入15x15棋盘数组，返回AI的下棋位置和更新后的棋盘
        board: 15x15的二维数组，0表示空位，1表示对手，2表示AI
        返回: (row, col, new_board) 或 None如果没有合法移动
        """
        start_time = time.time()
        
        # 创建根节点
        root = MCTSNode(board, self.player)
        
        # 如果没有合法移动
        if not root.get_legal_moves():
            return None
        
        # 第一步下中心
        if len(root.get_legal_moves()) == 1 and root.get_legal_moves()[0] == (7, 7):
            new_board = copy.deepcopy(board)
            new_board[7][7] = self.player
            return (7, 7, new_board)
        
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
            result = self.simulate(node)
            
            # 4. 反向传播
            self.backpropagate(node, result)
            
            iteration += 1
        
        # 选择最佳移动
        if not root.children:
            return None
        
        best_child = max(root.children, key=lambda c: c.visits)
        row, col = best_child.move
        
        new_board = copy.deepcopy(board)
        new_board[row][col] = self.player
        
        print(f"MCTS完成 {iteration} 次迭代，选择位置 ({row}, {col})")
        print(f"最佳移动访问次数: {best_child.visits}, 胜率: {best_child.wins/best_child.visits:.3f}")
        
        return (row, col, new_board)
    
    def select(self, node):
        """选择阶段：使用UCB1选择最佳子节点"""
        while not node.is_terminal():
            if node.untried_moves:
                return node
            else:
                node = max(node.children, key=lambda c: c.ucb1_value())
        return node
    
    def simulate(self, node):
        """模拟阶段：随机对局直到游戏结束"""
        current_board = copy.deepcopy(node.board)
        current_player = node.player
        
        # 检查当前节点是否已经有获胜者
        winner = node.check_winner()
        if winner:
            return 1 if winner == self.player else 0
        
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
                return 1 if current_player == self.player else 0
            
            # 切换玩家
            current_player = 3 - current_player
            moves_count += 1
        
        # 如果没有明确胜负，使用简单评估
        return self.evaluate_simulation_result(current_board)
    
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
    
    def evaluate_simulation_result(self, board):
        """评估模拟结果（当没有明确胜负时）"""
        # 简单的位置评估：更倾向于中心位置
        ai_score = 0
        opponent_score = 0
        
        for i in range(15):
            for j in range(15):
                if board[i][j] == self.player:
                    ai_score += self.position_value(i, j)
                elif board[i][j] == self.opponent:
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
            if node.player != self.player:
                result = 1 - result
            node = node.parent


# 使用示例
if __name__ == "__main__":
    # 创建MCTS AI实例
    mcts_ai = GomokuMCTS(player=2, opponent=1, iterations=1000, max_time=3.0)
    
    # 创建测试棋盘
    board = [[0 for _ in range(15)] for _ in range(15)]
    
    # 模拟几步棋
    board[7][7] = 1  # 对手先下中心
    board[7][8] = 1  # 对手连续下棋
    board[8][7] = 2  # AI下棋
    
    print("当前棋盘状态:")
    for i, row in enumerate(board):
        print(f"{i:2d}: " + ' '.join(str(x) for x in row))
    
    # AI计算下一步
    print("\nMCTS AI 开始思考...")
    result = mcts_ai.get_next_move(board)
    
    if result:
        row, col, new_board = result
        print(f"\nAI选择位置: ({row}, {col})")
        print("更新后棋盘:")
        for i, board_row in enumerate(new_board):
            print(f"{i:2d}: " + ' '.join(str(x) for x in board_row))
    else:
        print("没有可用移动")