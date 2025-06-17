""" 
AI相关功能 - MCTS版本 (高质量版) - 修复版
"""
import math
import copy
import time
import random
from collections import defaultdict
from utils.constants import *
from utils.chessboard import ChessBoard
from utils.gomoku_ai import GomokuAI

class AdvancedPatternEvaluator:
    """高级五子棋模式评估器"""
    
    def __init__(self):
        # 更详细的模式评分系统
        self.attack_patterns = {
            # 五连 - 必胜
            'OOOOO': 1000000,
            # 活四 - 必胜
            '_OOOO_': 100000,
            # 冲四 - 很强
            'XOOOO_': 10000, '_OOOOX': 10000,
            # 活三 - 强
            '_OOO_': 5000, '__OOO__': 8000,
            # 眠三
            'XOOO_': 1000, '_OOOX': 1000, 'XO_OO_': 800, '_OO_OX': 800,
            # 活二
            '_OO_': 200, '__OO__': 300,
            # 眠二
            'XOO_': 50, '_OOX': 50,
        }
        
        self.defense_patterns = {
            # 对手的威胁模式 - 必须防守
            'XXXXX': 500000,
            '_XXXX_': 50000,
            'OXXXX_': 10000, '_XXXXO': 10000,
            '_XXX_': 5000, '__XXX__': 8000,
            'OXXX_': 1000, '_XXXO': 1000,
        }
        
        # 特殊战术模式
        self.tactical_patterns = {
            # 双三
            'double_three': 15000,
            # 三三禁手检测
            'forbidden_three': -50000,
            # 四四胜型
            'double_four': 200000,
        }
    
    def evaluate_position(self, board, row, col, player):
        """全面评估位置价值"""
        if board[row][col] != 0:
            return -1000000  # 非法位置
        
        # 临时放置棋子
        board[row][col] = player
        
        # 综合评分
        attack_score = self._evaluate_attack_patterns(board, row, col, player)
        defense_score = self._evaluate_defense_patterns(board, row, col, player)
        tactical_score = self._evaluate_tactical_patterns(board, row, col, player)
        position_score = self._evaluate_position_value(board, row, col)
        
        # 恢复棋盘
        board[row][col] = 0
        
        total_score = attack_score + defense_score + tactical_score + position_score
        return total_score
    
    def _evaluate_attack_patterns(self, board, row, col, player):
        """评估攻击模式"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            line = self._get_line_string(board, row, col, dx, dy, player)
            for pattern, value in self.attack_patterns.items():
                if pattern in line:
                    score += value
        
        return score
    
    def _evaluate_defense_patterns(self, board, row, col, player):
        """评估防守模式"""
        score = 0
        opponent = 3 - player
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # 临时放置对手棋子来检查威胁
        board[row][col] = opponent
        
        for dx, dy in directions:
            line = self._get_line_string(board, row, col, dx, dy, opponent)
            for pattern, value in self.defense_patterns.items():
                if pattern in line:
                    score += value
        
        # 恢复
        board[row][col] = player
        return score
    
    def _evaluate_tactical_patterns(self, board, row, col, player):
        """评估战术模式（双三、四四等）"""
        score = 0
        
        # 检查是否形成双活三
        three_count = self._count_active_threes(board, row, col, player)
        if three_count >= 2:
            score += self.tactical_patterns['double_three']
        
        # 检查是否形成双四
        four_count = self._count_fours(board, row, col, player)
        if four_count >= 2:
            score += self.tactical_patterns['double_four']
        
        return score
    
    def _evaluate_position_value(self, board, row, col):
        """评估位置本身的价值"""
        # 距离中心的价值
        center_distance = math.sqrt((row - 7)**2 + (col - 7)**2)
        center_value = max(0, 100 - center_distance * 5)
        
        # 周围棋子密度
        density_value = self._calculate_density(board, row, col)
        
        return center_value + density_value
    
    def _get_line_string(self, board, row, col, dx, dy, player):
        """获取某方向的棋子串表示"""
        line = []
        
        # 向负方向扩展
        for i in range(4, 0, -1):
            r, c = row - i * dx, col - i * dy
            if 0 <= r < 15 and 0 <= c < 15:
                if board[r][c] == player:
                    line.append('O')
                elif board[r][c] == 0:
                    line.append('_')
                else:
                    line.append('X')
            else:
                line.append('X')  # 边界视为对手
        
        # 当前位置
        line.append('O')
        
        # 向正方向扩展
        for i in range(1, 5):
            r, c = row + i * dx, col + i * dy
            if 0 <= r < 15 and 0 <= c < 15:
                if board[r][c] == player:
                    line.append('O')
                elif board[r][c] == 0:
                    line.append('_')
                else:
                    line.append('X')
            else:
                line.append('X')
        
        return ''.join(line)
    
    def _count_active_threes(self, board, row, col, player):
        """计算活三数量"""
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            line = self._get_line_string(board, row, col, dx, dy, player)
            if '_OOO_' in line or '__OOO__' in line:
                count += 1
        
        return count
    
    def _count_fours(self, board, row, col, player):
        """计算四连数量"""
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            line = self._get_line_string(board, row, col, dx, dy, player)
            if 'OOOO' in line:
                count += 1
        
        return count
    
    def _calculate_density(self, board, row, col):
        """计算周围棋子密度"""
        density = 0
        for i in range(max(0, row-2), min(15, row+3)):
            for j in range(max(0, col-2), min(15, col+3)):
                if board[i][j] != 0:
                    distance = max(abs(i-row), abs(j-col))
                    density += (3 - distance) * 10
        return density

class EnhancedMCTSNode:
    """增强的MCTS节点"""
    
    def __init__(self, board, player, move=None, parent=None):
        self.board = board
        self.player = player
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.squared_wins = 0.0  # 用于计算方差
        self.untried_moves = None
        self._is_terminal = None
        self.urgency_score = 0  # 紧急程度评分
        
    def get_legal_moves(self):
        """获取合法移动（更智能的候选生成）"""
        if self.untried_moves is not None:
            return self.untried_moves
        
        evaluator = AdvancedPatternEvaluator()
        candidates = []
        
        # 如果棋盘为空，返回中心位置
        if all(self.board[i][j] == 0 for i in range(15) for j in range(15)):
            self.untried_moves = [(7, 7)]
            return self.untried_moves
        
        # 生成候选位置并评估
        for i in range(15):
            for j in range(15):
                if self.board[i][j] == 0:
                    # 检查是否在已有棋子附近
                    if self._is_near_stones(i, j):
                        try:
                            score = evaluator.evaluate_position(self.board, i, j, self.player)
                            candidates.append((score, (i, j)))
                        except:
                            # 如果评估失败，使用基础分数
                            candidates.append((0, (i, j)))
        
        # 按评分排序，选择最有前途的候选
        candidates.sort(reverse=True, key=lambda x: x[0])
        
        # 取前50个候选（如果有的话）
        self.untried_moves = [move for _, move in candidates[:50]]
        return self.untried_moves
    
    def _is_near_stones(self, row, col, radius=3):
        """检查位置是否在已有棋子附近"""
        for i in range(max(0, row-radius), min(15, row+radius+1)):
            for j in range(max(0, col-radius), min(15, col+radius+1)):
                if self.board[i][j] != 0:
                    return True
        return False
    
    def is_terminal(self):
        """检查终端状态"""
        if self._is_terminal is not None:
            return self._is_terminal
        
        winner = self.check_winner()
        if winner is not None:
            self._is_terminal = True
            return True
        
        # 检查是否还有合法移动
        legal_moves = self.get_legal_moves()
        self._is_terminal = len(legal_moves) == 0
        return self._is_terminal
    
    def check_winner(self):
        """检查获胜者"""
        if self.move is None:
            return None
        
        row, col = self.move
        player = self.board[row][col]
        if player == 0:
            return None
        
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
                return player
        return None
    
    def add_child(self, move):
        """添加子节点"""
        new_board = copy.deepcopy(self.board)
        new_board[move[0]][move[1]] = self.player
        child = EnhancedMCTSNode(new_board, 3 - self.player, move, self)
        self.children.append(child)
        return child
    
    def update(self, result):
        """更新节点统计"""
        self.visits += 1
        self.wins += result
        self.squared_wins += result * result
    
    def ucb1_value(self, c=1.414):
        """计算UCB1值（带方差考虑）"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        
        # 添加方差项
        if self.visits > 1:
            variance = (self.squared_wins / self.visits) - (exploitation ** 2)
            if variance > 0:  # 确保方差为正
                variance_bonus = math.sqrt(variance / self.visits)
                exploration += variance_bonus * 0.1
        
        return exploitation + exploration + self.urgency_score
    
    def get_win_rate(self):
        """获取胜率"""
        return self.wins / self.visits if self.visits > 0 else 0

class HighQualityMCTSEngine:
    """高质量MCTS引擎"""
    
    def __init__(self, iterations=3000, max_time=8.0, c_param=1.414):
        self.iterations = iterations
        self.max_time = max_time
        self.c_param = c_param
        self.evaluator = AdvancedPatternEvaluator()
        self.currentI = 0
        self.currentJ = 0
        
        # 高质量参数
        self.max_simulation_depth = 60
        self.min_visits_for_expansion = 3
        self.progressive_widening_factor = 0.4
        
    def get_next_move(self, board, player):
        """获取下一步移动"""
        start_time = time.time()
        
        # 转换棋盘格式
        converted_board = self.convert_board_format(board)
        
        # 创建根节点
        mcts_player = 1 if player == 1 else 2
        root = EnhancedMCTSNode(converted_board, mcts_player)
        
        # 特殊情况处理
        legal_moves = root.get_legal_moves()
        if not legal_moves:
            return (7, 7)
        
        # 紧急移动检查（必胜或必防）
        urgent_move = self._check_urgent_moves(converted_board, mcts_player)
        if urgent_move:
            self.currentI, self.currentJ = urgent_move
            return urgent_move
        
        # 开局策略
        if self._is_early_game(converted_board):
            move = self._get_opening_move(converted_board, mcts_player)
            if move:
                self.currentI, self.currentJ = move
                return move
        
        # MCTS主循环
        iteration = 0
        
        while iteration < self.iterations and time.time() - start_time < self.max_time:
            try:
                # 1. 选择
                node = self._enhanced_select(root)
                
                # 2. 扩展（渐进扩展）
                if not node.is_terminal():
                    if (node.visits >= self.min_visits_for_expansion and 
                        hasattr(node, 'untried_moves') and node.untried_moves):
                        # 渐进扩展：根据访问次数决定扩展数量
                        max_children = max(1, int(node.visits ** self.progressive_widening_factor))
                        if len(node.children) < max_children and node.untried_moves:
                            move = node.untried_moves.pop(0)
                            node = node.add_child(move)
                
                # 3. 高质量模拟
                result = self._enhanced_simulate(node, mcts_player)
                
                # 4. 反向传播
                self._backpropagate(node, result)
                
                iteration += 1
                
                # 定期输出进度
                if iteration % 500 == 0 and root.children:
                    best_child = max(root.children, key=lambda c: c.visits)
                    print(f"迭代 {iteration}: 最佳移动 {best_child.move}, 胜率 {best_child.get_win_rate():.3f}")
                    
            except Exception as e:
                print(f"MCTS迭代出错: {e}")
                break
        
        # 选择最佳移动（修复排序问题）
        if not root.children:
            return (7, 7)
        
        best_child = self._select_best_move(root)
        self.currentI, self.currentJ = best_child.move
        
        print(f"高质量MCTS完成 {iteration} 次迭代")
        print(f"最终选择: {best_child.move}, 访问次数: {best_child.visits}, 胜率: {best_child.get_win_rate():.3f}")
        
        return best_child.move
    
    def _check_urgent_moves(self, board, player):
        """检查紧急移动（必胜或必防）"""
        opponent = 3 - player
        
        # 检查是否有必胜移动
        for i in range(15):
            for j in range(15):
                if board[i][j] == 0:
                    board[i][j] = player
                    if self._check_winner_at_position(board, i, j, player):
                        board[i][j] = 0
                        print(f"发现必胜移动: ({i}, {j})")
                        return (i, j)
                    board[i][j] = 0
        
        # 检查是否需要防守
        for i in range(15):
            for j in range(15):
                if board[i][j] == 0:
                    board[i][j] = opponent
                    if self._check_winner_at_position(board, i, j, opponent):
                        board[i][j] = 0
                        print(f"发现必防移动: ({i}, {j})")
                        return (i, j)
                    board[i][j] = 0
        
        return None
    
    def _check_winner_at_position(self, board, row, col, player):
        """检查指定位置是否获胜"""
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
    
    def _enhanced_select(self, node):
        """增强的选择策略"""
        while not node.is_terminal():
            if hasattr(node, 'untried_moves') and node.untried_moves:
                return node
            elif node.children:
                # 使用更复杂的选择策略
                node = max(node.children, key=lambda c: c.ucb1_value(self.c_param))
            else:
                return node
        return node
    
    def _enhanced_simulate(self, node, ai_player):
        """增强的模拟策略"""
        current_board = copy.deepcopy(node.board)
        current_player = node.player
        
        # 检查当前是否已有获胜者
        if node.move:
            if self._check_winner_at_position(current_board, node.move[0], node.move[1], current_board[node.move[0]][node.move[1]]):
                winner = current_board[node.move[0]][node.move[1]]
                return 1.0 if winner == ai_player else 0.0
        
        # 智能模拟
        moves_count = 0
        
        while moves_count < self.max_simulation_depth:
            # 获取高质量候选移动
            legal_moves = self._get_quality_simulation_moves(current_board, current_player)
            if not legal_moves:
                break
            
            # 使用高质量策略选择移动
            move = self._choose_quality_move(current_board, legal_moves, current_player)
            
            # 执行移动
            current_board[move[0]][move[1]] = current_player
            
            # 检查是否获胜
            if self._check_winner_at_position(current_board, move[0], move[1], current_player):
                return 1.0 if current_player == ai_player else 0.0
            
            # 切换玩家
            current_player = 3 - current_player
            moves_count += 1
        
        # 使用高级评估
        return self._advanced_position_evaluation(current_board, ai_player)
    
    def _get_quality_simulation_moves(self, board, player):
        """获取高质量模拟移动"""
        candidates = []
        
        for i in range(15):
            for j in range(15):
                if board[i][j] == 0:
                    # 检查是否在棋子附近
                    if self._is_near_stones(board, i, j, radius=2):
                        try:
                            score = self.evaluator.evaluate_position(board, i, j, player)
                            candidates.append((score, (i, j)))
                        except:
                            candidates.append((0, (i, j)))
        
        # 排序并返回前15个候选
        candidates.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in candidates[:15]]
    
    def _choose_quality_move(self, board, moves, player):
        """选择高质量移动"""
        if not moves:
            return (7, 7)
            
        # 检查立即获胜
        for move in moves:
            board[move[0]][move[1]] = player
            if self._check_winner_at_position(board, move[0], move[1], player):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 0
        
        # 检查阻止对手获胜
        opponent = 3 - player
        for move in moves:
            board[move[0]][move[1]] = opponent
            if self._check_winner_at_position(board, move[0], move[1], opponent):
                board[move[0]][move[1]] = 0
                return move
            board[move[0]][move[1]] = 0
        
        # 使用评估函数选择最佳移动（带随机性）
        best_moves = []
        for move in moves:
            try:
                score = self.evaluator.evaluate_position(board, move[0], move[1], player)
                best_moves.append((score, move))
            except:
                best_moves.append((0, move))
        
        best_moves.sort(reverse=True, key=lambda x: x[0])
        
        # 在前3个最佳移动中随机选择
        top_moves = [move for _, move in best_moves[:3]]
        return random.choice(top_moves) if top_moves else random.choice(moves)
    
    def _is_near_stones(self, board, row, col, radius=2):
        """检查是否在棋子附近"""
        for i in range(max(0, row-radius), min(15, row+radius+1)):
            for j in range(max(0, col-radius), min(15, col+radius+1)):
                if board[i][j] != 0:
                    return True
        return False
    
    def _advanced_position_evaluation(self, board, ai_player):
        """高级位置评估"""
        ai_total = 0
        opponent_total = 0
        opponent = 3 - ai_player
        
        # 评估每个空位的价值
        for i in range(15):
            for j in range(15):
                if board[i][j] == 0 and self._is_near_stones(board, i, j, radius=2):
                    try:
                        ai_value = self.evaluator.evaluate_position(board, i, j, ai_player)
                        opp_value = self.evaluator.evaluate_position(board, i, j, opponent)
                        ai_total += max(0, ai_value)
                        opponent_total += max(0, opp_value)
                    except:
                        continue
        
        # 计算相对优势
        total = ai_total + opponent_total
        if total == 0:
            return 0.5
        
        ai_ratio = ai_total / total
        
        # 添加一些随机性避免过度确定
        noise = random.uniform(-0.03, 0.03)
        return max(0.1, min(0.9, ai_ratio + noise))
    
    def _select_best_move(self, root):
        """选择最佳移动（修复排序问题）"""
        if not root.children:
            return None
        
        # 修复: 确保正确排序数值对而不是节点对象
        scored_children = []
        
        for child in root.children:
            if child.visits > 0:
                win_rate = child.get_win_rate()
                visit_score = child.visits / max(1, root.visits) * 100
                
                try:
                    ucb_score = child.ucb1_value(0)  # 不带探索的UCB
                except:
                    ucb_score = 0
                
                # 综合评分
                composite_score = win_rate * 0.6 + visit_score * 0.3 + ucb_score * 0.1
                scored_children.append((composite_score, child))
        
        if scored_children:
            # 修复: 按分数排序，不是按节点排序
            scored_children.sort(key=lambda x: x[0], reverse=True)
            return scored_children[0][1]
        
        # 备用策略：选择访问次数最多的
        return max(root.children, key=lambda c: c.visits)
    
    def _backpropagate(self, node, result):
        """反向传播"""
        while node is not None:
            node.update(result)
            if node.parent and node.parent.player != node.player:
                result = 1.0 - result
            node = node.parent
    
    def convert_board_format(self, board):
        """转换棋盘格式"""
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
    
    def _is_early_game(self, board):
        """判断是否为开局"""
        piece_count = sum(1 for i in range(15) for j in range(15) if board[i][j] != 0)
        return piece_count <= 6
    
    def _get_opening_move(self, board, player):
        """获取开局移动"""
        center = (7, 7)
        
        # 第一步下中心
        if board[center[0]][center[1]] == 0:
            piece_count = sum(1 for i in range(15) for j in range(15) if board[i][j] != 0)
            if piece_count == 0:
                return center
        
        # 开局策略：在中心附近找最佳位置
        candidates = []
        for radius in range(1, 4):
            for di in range(-radius, radius + 1):
                for dj in range(-radius, radius + 1):
                    if abs(di) == radius or abs(dj) == radius:
                        ni, nj = center[0] + di, center[1] + dj
                        if (0 <= ni < 15 and 0 <= nj < 15 and board[ni][nj] == 0):
                            try:
                                score = self.evaluator.evaluate_position(board, ni, nj, player)
                                candidates.append((score, (ni, nj)))
                            except:
                                candidates.append((0, (ni, nj)))
        
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        
        return None

class MCTSAIPlayer(GomokuAI):
    """基于高质量MCTS算法的AI玩家"""
    
    def __init__(self, iterations=3000, max_time=8.0, c_param=1.414):
        self.thinking = False
        self.iterations = iterations
        self.max_time = max_time
        self.engine = HighQualityMCTSEngine(iterations, max_time, c_param)
    
    def convert_board(self, board, player_side):
        """转换棋盘格式"""
        converted = []
        for row in board:
            converted_row = []
            for cell in row:
                if cell == PIECE_EMPTY:
                    converted_row.append(0)
                elif cell == PIECE_BLACK:
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
        
        # 更新棋盘状态
        if 0 <= row < board_size and 0 <= col < board_size and board_inner[row][col] == PIECE_EMPTY:
            chessboard.place_stone(row, col, player_side)
        
        return chessboard
    
    def get_move(self, board, board_size, player_side):
        """获取AI的下一步移动"""
        self.thinking = True
        try:
            print("高质量MCTS AI开始思考...")
            
            # 转换棋盘表示
            converted_board = self.convert_board(board, player_side)
            
            # 创建新引擎实例
            self.engine = HighQualityMCTSEngine(self.iterations, self.max_time)
            
            # 空棋盘处理
            if all(cell == 0 for row in converted_board for cell in row):
                center = board_size // 2
                return center, center
            
            # 确定玩家标识
            player = 1 if player_side == PLAYER_BLACK else -1
            
            # 执行高质量MCTS搜索
            row, col = self.engine.get_next_move(converted_board, player)
            
            print(f"高质量MCTS AI计算结果: ({row}, {col})")
            return row, col
            
        except Exception as e:
            print(f"高质量MCTS AI计算出错: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_move(board, board_size)
        finally:
            self.thinking = False
    
    def _get_fallback_move(self, board, board_size):
        """备用策略"""
        center = board_size // 2
        
        # 优先在中心附近寻找
        for radius in range(min(5, board_size // 2 + 1)):
            candidates = []
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r, c = center + dr, center + dc
                    if (0 <= r < board_size and 0 <= c < board_size and 
                        board[r][c] == PIECE_EMPTY):
                        candidates.append((r, c))
            
            if candidates:
                return random.choice(candidates)
        
        return 0, 0