import copy
import time

class GomokuAI:
    def __init__(self, player=2, opponent=1, max_depth=4, max_time=5.0):
        """
        五子棋AI算法，使用α-β剪枝
        player: AI棋子标识 (默认2)
        opponent: 对手棋子标识 (默认1)
        max_depth: 最大搜索深度
        max_time: 最大思考时间(秒)
        """
        self.player = player
        self.opponent = opponent
        self.max_depth = max_depth
        self.max_time = max_time
        self.start_time = 0
        
        # 棋型评分表
        self.patterns = {
            # AI棋型评分 (正分)
            (5, 0): 1000000,   # 五连
            (4, 1): 50000,     # 活四
            (4, 0): 10000,     # 冲四
            (3, 1): 5000,      # 活三
            (3, 0): 1000,      # 眠三
            (2, 1): 500,       # 活二
            (2, 0): 100,       # 眠二
            (1, 1): 50,        # 活一
            
            # 对手棋型评分 (负分，防守)
            (-5, 0): -2000000, # 对手五连
            (-4, 1): -100000,  # 对手活四
            (-4, 0): -20000,   # 对手冲四
            (-3, 1): -10000,   # 对手活三
            (-3, 0): -2000,    # 对手眠三
            (-2, 1): -1000,    # 对手活二
            (-2, 0): -200,     # 对手眠二
        }

    def get_next_move(self, board):
        """
        输入15x15棋盘数组，返回AI的下棋位置和更新后的棋盘
        board: 15x15的二维数组，0表示空位，1表示对手，2表示AI
        返回: (row, col, new_board) 或 None如果没有合法移动
        """
        self.start_time = time.time()
        
        # 检查是否有空位
        empty_positions = self.get_empty_positions(board)
        if not empty_positions:
            return None
        
        # 第一步下中心
        if len(empty_positions) == 225:  # 棋盘全空
            new_board = copy.deepcopy(board)
            new_board[7][7] = self.player
            return (7, 7, new_board)
        
        # α-β剪枝搜索最佳移动
        best_move = self.alphabeta_search(board)
        
        if best_move:
            row, col = best_move
            new_board = copy.deepcopy(board)
            new_board[row][col] = self.player
            return (row, col, new_board)
        
        return None

    def alphabeta_search(self, board):
        """α-β剪枝搜索"""
        candidate_moves = self.get_candidate_moves(board)
        if not candidate_moves:
            return None
            
        # 移动排序优化
        candidate_moves = self.order_moves(board, candidate_moves)
        
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in candidate_moves:
            if time.time() - self.start_time > self.max_time:
                break
                
            row, col = move
            board[row][col] = self.player
            
            score = self.alphabeta(board, self.max_depth - 1, alpha, beta, False)
            
            board[row][col] = 0  # 撤销移动
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        
        return best_move

    def alphabeta(self, board, depth, alpha, beta, maximizing_player):
        """α-β剪枝递归搜索"""
        if time.time() - self.start_time > self.max_time:
            return self.evaluate_board(board)
            
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board)
        
        moves = self.get_candidate_moves(board)
        if not moves:
            return self.evaluate_board(board)
        
        if maximizing_player:  # AI回合
            max_eval = float('-inf')
            for move in moves:
                row, col = move
                board[row][col] = self.player
                eval_score = self.alphabeta(board, depth - 1, alpha, beta, False)
                board[row][col] = 0
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:  # β剪枝
                    break
            return max_eval
        else:  # 对手回合
            min_eval = float('inf')
            for move in moves:
                row, col = move
                board[row][col] = self.opponent
                eval_score = self.alphabeta(board, depth - 1, alpha, beta, True)
                board[row][col] = 0
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:  # α剪枝
                    break
            return min_eval

    def get_candidate_moves(self, board, radius=2):
        """获取候选移动位置"""
        candidates = set()
        
        # 如果棋盘为空，返回中心位置
        if all(board[i][j] == 0 for i in range(15) for j in range(15)):
            return [(7, 7)]
        
        # 在已有棋子周围寻找候选位置
        for i in range(15):
            for j in range(15):
                if board[i][j] != 0:
                    for di in range(-radius, radius + 1):
                        for dj in range(-radius, radius + 1):
                            ni, nj = i + di, j + dj
                            if (0 <= ni < 15 and 0 <= nj < 15 and 
                                board[ni][nj] == 0):
                                candidates.add((ni, nj))
        
        return list(candidates)

    def order_moves(self, board, moves):
        """移动排序，将更有希望的移动排在前面"""
        move_scores = []
        for move in moves:
            row, col = move
            board[row][col] = self.player
            score = self.evaluate_position(board, row, col, self.player)
            board[row][col] = 0
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True)
        return [move for score, move in move_scores]

    def evaluate_board(self, board):
        """评估整个棋盘"""
        score = 0
        for i in range(15):
            for j in range(15):
                if board[i][j] == self.player:
                    score += self.evaluate_position(board, i, j, self.player)
                elif board[i][j] == self.opponent:
                    score += self.evaluate_position(board, i, j, self.opponent)
        return score

    def evaluate_position(self, board, row, col, player):
        """评估某个位置的分数"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 横、竖、主对角、副对角
        
        for dx, dy in directions:
            # 统计该方向上的连子情况
            count, left_empty, right_empty = self.count_direction(board, row, col, dx, dy, player)
            
            # 计算活子数量(两端空位数)
            empty_ends = left_empty + right_empty
            if empty_ends > 2:
                empty_ends = 2
            
            # 根据棋型模式计算分数
            pattern_key = (count if player == self.player else -count, empty_ends)
            if pattern_key in self.patterns:
                score += self.patterns[pattern_key]
        
        return score

    def count_direction(self, board, row, col, dx, dy, player):
        """统计某个方向上的连子数量和两端空位情况"""
        count = 1  # 包含当前位置
        
        # 向一个方向统计
        left_empty = 0
        i, j = row - dx, col - dy
        while 0 <= i < 15 and 0 <= j < 15:
            if board[i][j] == player:
                count += 1
            elif board[i][j] == 0:
                left_empty = 1
                break
            else:
                break
            i, j = i - dx, j - dy
        
        # 向另一个方向统计
        right_empty = 0
        i, j = row + dx, col + dy
        while 0 <= i < 15 and 0 <= j < 15:
            if board[i][j] == player:
                count += 1
            elif board[i][j] == 0:
                right_empty = 1
                break
            else:
                break
            i, j = i + dx, j + dy
        
        return count, left_empty, right_empty

    def is_game_over(self, board):
        """检查游戏是否结束"""
        # 检查是否有五连
        for i in range(15):
            for j in range(15):
                if board[i][j] != 0:
                    if self.check_five_in_row(board, i, j, board[i][j]):
                        return True
        return False

    def check_five_in_row(self, board, row, col, player):
        """检查是否有五连"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            # 向一个方向检查
            i, j = row + dx, col + dy
            while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
                count += 1
                i, j = i + dx, j + dy
            
            # 向另一个方向检查
            i, j = row - dx, col - dy
            while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
                count += 1
                i, j = i - dx, j - dy
            
            if count >= 5:
                return True
        
        return False

    def get_empty_positions(self, board):
        """获取所有空位"""
        empty = []
        for i in range(15):
            for j in range(15):
                if board[i][j] == 0:
                    empty.append((i, j))
        return empty


# 使用示例
if __name__ == "__main__":
    # 创建AI实例
    ai = GomokuAI(player=2, opponent=1, max_depth=4)
    
    # 创建测试棋盘
    board = [[0 for _ in range(15)] for _ in range(15)]
    
    # 模拟几步棋
    board[7][7] = 1  # 对手先下中心附近
    board[7][8] = 1  # 对手连续下棋
    
    print("当前棋盘状态:")
    for row in board:
        print(' '.join(str(x) for x in row))
    
    # AI计算下一步
    result = ai.get_next_move(board)
    if result:
        row, col, new_board = result
        print(f"\nAI选择位置: ({row}, {col})")
        print("更新后棋盘:")
        for board_row in new_board:
            print(' '.join(str(x) for x in board_row))
    else:
        print("没有可用移动")