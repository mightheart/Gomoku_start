"""游戏统计模块"""
import time
from utils.constants import PLAYER_BLACK, PLAYER_WHITE, MAX_UNDO_STEPS

class GameStatistics:
    """游戏统计管理器"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置统计数据"""
        self.game_start_time = time.time()
        self.current_player_start_time = time.time()
        self.player_black_total_time = 0.0
        self.player_white_total_time = 0.0
        self.move_count = 0
        self.move_history = []
        self.undo_count = 0
    
    def update_player_time(self, current_player, game_over=False):
        """更新当前玩家用时"""
        if game_over:
            return
        
        current_time = time.time()
        time_spent = current_time - self.current_player_start_time
        
        if current_player == PLAYER_BLACK:
            self.player_black_total_time += time_spent
        else:
            self.player_white_total_time += time_spent
        
        self.current_player_start_time = current_time
    
    def add_move(self, row, col, player):
        """添加移动记录"""
        self.move_history.append((row, col, player))
        self.move_count += 1
    
    def undo_moves(self, steps_to_undo):
        """撤销移动"""
        undone_moves = []
        for _ in range(steps_to_undo):
            if self.move_history:
                move = self.move_history.pop()
                undone_moves.append(move)
                self.move_count -= 1
        
        self.undo_count += 1
        return undone_moves
    
    def can_undo(self):
        """检查是否可以悔棋"""
        return self.undo_count < MAX_UNDO_STEPS and len(self.move_history) > 0
    
    def get_game_data(self):
        """获取游戏数据用于UI显示"""
        game_duration = time.time() - self.game_start_time
        return {
            'game_duration': game_duration,
            'move_count': self.move_count,
            'black_time': self.player_black_total_time,
            'white_time': self.player_white_total_time,
            'undo_count': self.undo_count
        }
    
    def get_final_statistics(self):
        """获取最终统计信息"""
        game_duration = time.time() - self.game_start_time
        
        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        
        stats = f"📊 Game Statistics 📊\n"
        stats += f"Total Time: {format_time(game_duration)}\n"
        stats += f"Total Moves: {self.move_count}\n"
        stats += f"Black Time: {format_time(self.player_black_total_time)}\n"
        stats += f"White Time: {format_time(self.player_white_total_time)}\n"
        stats += f"Undos Used: {self.undo_count} times"
        
        return stats