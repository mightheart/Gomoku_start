from .constants import *
from .utils_minimax import *
import math

class MinimaxAIEngine:
    def __init__(self, depth=3):
        self.depth = depth
        self.board_size = BOARD_SIZE
        self.boardMap = [[0 for j in range(self.board_size)] for i in range(self.board_size)]
        self.currentI = -1
        self.currentJ = -1
        self.nextBound = {}
        self.boardValue = 0
        self.turn = 0
        self.lastPlayed = 0
        self.emptyCells = self.board_size * self.board_size
        self.patternDict = create_pattern_dict()
        self.zobristTable = init_zobrist()
        self.update_TTable = update_TTable
        self.rollingHash = 0
        self.TTable = {}
    
    
    def isValid(self, i, j, state=True):
        if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size:
            return False
        if state:
            return self.boardMap[i][j] == 0
        return True

    def setState(self, i, j, state):
        self.boardMap[i][j] = state
        self.lastPlayed = state

    def countDirection(self, i, j, xdir, ydir, state):
        count = 0
        for step in range(1, 5):
            new_i, new_j = i + ydir * step, j + xdir * step
            if not (0 <= new_i < self.board_size and 0 <= new_j < self.board_size):
                break
            if self.boardMap[new_i][new_j] == state:
                count += 1
            else:
                break
        return count

    def isFive(self, i, j, state):
        directions = [[(-1, 0), (1, 0)],
                      [(0, -1), (0, 1)],
                      [(-1, 1), (1, -1)],
                      [(-1, -1), (1, 1)]]
        
        for axis in directions:
            axis_count = 1
            for (xdir, ydir) in axis:
                axis_count += self.countDirection(i, j, xdir, ydir, state)
                if axis_count >= 5:
                    return True
        return False

    def childNodes(self, bound):
        for pos in sorted(bound.items(), key=lambda el: el[1], reverse=True):
            yield pos[0]

    def updateBound(self, new_i, new_j, bound):
        played = (new_i, new_j)
        if played in bound:
            bound.pop(played)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                     (-1, 1), (1, -1), (-1, -1), (1, 1)]
        for dx, dy in directions:
            new_row, new_col = new_i + dy, new_j + dx
            if self.isValid(new_row, new_col) and (new_row, new_col) not in bound:
                bound[(new_row, new_col)] = 0

    def countPattern(self, i_0, j_0, pattern, score, bound, flag):
        directions = [(1, 0), (1, 1), (0, 1), (-1, 1)]
        length = len(pattern)
        count = 0

        for dx, dy in directions:
            # Calculate steps back
            if dx * dy == 0:
                steps_back = dx * min(5, j_0) + dy * min(5, i_0)
            elif dx == 1:
                steps_back = min(5, j_0, i_0)
            else:
                steps_back = min(5, self.board_size-1-j_0, i_0)
            
            i_start = i_0 - steps_back * dy
            j_start = j_0 - steps_back * dx

            z = 0
            while z <= steps_back:
                i_new = i_start + z * dy
                j_new = j_start + z * dx
                index = 0
                remember = []
                
                while index < length:
                    ni, nj = i_new + index * dy, j_new + index * dx
                    if not (0 <= ni < self.board_size and 0 <= nj < self.board_size):
                        break
                    if self.boardMap[ni][nj] != pattern[index]:
                        break
                    if self.boardMap[ni][nj] == 0:
                        remember.append((ni, nj))
                    index += 1
                
                if index == length:
                    count += 1
                    for pos in remember:
                        if pos not in bound:
                            bound[pos] = 0
                        bound[pos] += flag * score
                    z += index
                else:
                    z += 1

        return count

    def evaluate(self, i, j, board_value, turn, bound):
        value_before = 0
        value_after = 0
        
        for pattern in self.patternDict:
            score = self.patternDict[pattern]
            value_before += self.countPattern(i, j, pattern, abs(score), bound, -1) * score
            
            # Make move temporarily
            original_state = self.boardMap[i][j]
            self.boardMap[i][j] = turn
            value_after += self.countPattern(i, j, pattern, abs(score), bound, 1) * score
            self.boardMap[i][j] = original_state  # Restore

        return board_value + value_after - value_before

    def alphaBetaPruning(self, depth, board_value, bound, alpha, beta, maximizingPlayer):
        # 终止条件
        if depth <= 0 or self.checkResult() is not None:
            return board_value
        
        # 置换表查找
        if self.rollingHash in self.TTable and self.TTable[self.rollingHash][1] >= depth:
            return self.TTable[self.rollingHash][0]
        
        if maximizingPlayer:
            max_val = -math.inf
            for child in self.childNodes(bound):
                i, j = child
                new_bound = dict(bound)
                new_val = self.evaluate(i, j, board_value, 1, new_bound)
                
                # 更新棋盘状态
                self.boardMap[i][j] = 1
                self.rollingHash ^= self.zobristTable[i][j][0]
                self.updateBound(i, j, new_bound)
                
                # 递归搜索
                eval_val = self.alphaBetaPruning(depth-1, new_val, new_bound, alpha, beta, False)
                if eval_val > max_val:
                    max_val = eval_val
                    if depth == self.depth:
                        self.currentI = i
                        self.currentJ = j
                        self.boardValue = eval_val
                        self.nextBound = new_bound
                
                alpha = max(alpha, eval_val)
                
                # 恢复棋盘状态
                self.boardMap[i][j] = 0
                self.rollingHash ^= self.zobristTable[i][j][0]
                
                if beta <= alpha:
                    break
            
            self.update_TTable(self.TTable, self.rollingHash, max_val, depth)
            return max_val
        
        else:
            min_val = math.inf
            for child in self.childNodes(bound):
                i, j = child
                new_bound = dict(bound)
                new_val = self.evaluate(i, j, board_value, -1, new_bound)
                
                # 更新棋盘状态
                self.boardMap[i][j] = -1
                self.rollingHash ^= self.zobristTable[i][j][1]
                self.updateBound(i, j, new_bound)
                
                # 递归搜索
                eval_val = self.alphaBetaPruning(depth-1, new_val, new_bound, alpha, beta, True)
                if eval_val < min_val:
                    min_val = eval_val
                    if depth == self.depth:
                        self.currentI = i
                        self.currentJ = j
                        self.boardValue = eval_val
                        self.nextBound = new_bound
                
                beta = min(beta, eval_val)
                
                # 恢复棋盘状态
                self.boardMap[i][j] = 0
                self.rollingHash ^= self.zobristTable[i][j][1]
                
                if beta <= alpha:
                    break
            
            self.update_TTable(self.TTable, self.rollingHash, min_val, depth)
            return min_val

    def firstMove(self):
        center = self.board_size // 2
        self.currentI, self.currentJ = center, center
        self.setState(self.currentI, self.currentJ, 1)

    def checkResult(self):
        if self.currentI == -1 or self.currentJ == -1:
            return None
            
        if self.isFive(self.currentI, self.currentJ, self.lastPlayed):
            return self.lastPlayed
        
        if self.emptyCells <= 0:
            return 0
            
        return None