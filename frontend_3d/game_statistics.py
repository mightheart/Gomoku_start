"""游戏统计模块"""
import time
import random
from utils.constants import PLAYER_BLACK, PLAYER_WHITE, MAX_UNDO_STEPS

class GameStatistics:
    """游戏统计管理器"""
    
    def __init__(self, audio_manager=None):
        self.audio_manager = audio_manager
        self.reset()
    
    def set_audio_manager(self, audio_manager):
        """设置音频管理器"""
        self.audio_manager = audio_manager

    def reset(self):
        """重置统计数据"""
        self.game_start_time = time.time()
        self.current_player_start_time = time.time()
        self.player_black_total_time = 0.0
        self.player_white_total_time = 0.0
        self.move_count = 0
        self.move_history = []
        self.undo_count = 0
        self.last_player = None
        
        # 简化的语音控制
        self._催促_25s_played = False  # 是否已播放25秒催促
        self._催促_60s_played = False  # 是否已播放60秒催促
        self._last_voice_time = 0      # 上次播放语音的时间
        self._undo_voice_played = []   # 已播放过的悔棋语音索引列表
    
    def _can_play_voice(self):
        """检查是否可以播放语音（5秒冷却）"""
        return time.time() - self._last_voice_time >= 5
    
    def _play_voice(self, voice_type, volume=1):
        """播放语音并更新冷却时间"""
        if self.audio_manager and self._can_play_voice():
            # 使用新的统一接口
            result = self.audio_manager.play_ai_voice(voice_type, volume=volume)
            if result:  # 只有播放成功才更新冷却时间
                self._last_voice_time = time.time()
                print(f"播放语音: {voice_type}")
            else:
                print(f"播放语音失败: {voice_type}")
            return result
        else:
            print(f"语音冷却中，跳过播放: {voice_type}")
            return False


    def update_player_time(self, current_player, game_over=False, is_ai_enabled=False, ai_side=None):
        """更新当前玩家用时"""
        if game_over:
            return
        
        current_time = time.time()
        
        # 玩家切换逻辑
        if self.last_player != current_player:
            print(f"玩家切换: {self.last_player} -> {current_player}")
            
            # 先累加上一个玩家的用时（只在这里累加一次）
            if self.last_player is not None:
                time_spent = current_time - self.current_player_start_time
                if self.last_player == PLAYER_BLACK:
                    self.player_black_total_time += time_spent
                    print(f"黑棋累加时间: {time_spent:.1f}秒，总时间: {self.player_black_total_time:.1f}秒")
                else:
                    self.player_white_total_time += time_spent
                    print(f"白棋累加时间: {time_spent:.1f}秒，总时间: {self.player_white_total_time:.1f}秒")
            
            # 重置新玩家的计时
            self.current_player_start_time = current_time
            self.last_player = current_player
            
            # 判断是否切换到人类玩家，如果是则重置催促标记
            is_human_turn = not is_ai_enabled or current_player != ai_side
            if is_human_turn:
                self._催促_25s_played = False
                self._催促_60s_played = False
                print(f"切换到人类玩家，重置催促语音标记")
        
        # 催促语音逻辑 - 只在人类玩家回合触发
        is_human_turn = not is_ai_enabled or current_player != ai_side
        
        if is_human_turn:
            time_spent = current_time - self.current_player_start_time
            
            # 25秒催促
            if time_spent >= 25 and not self._催促_25s_played:
                if self._play_voice("催促", volume=1):
                    print(f"播放25秒催促语音成功")
                    self._催促_25s_played = True
            
            # 60秒催促
            elif time_spent >= 60 and not self._催促_60s_played:
                if self._play_voice("催促", volume=1):
                    print(f"播放60秒催促语音成功")
                    self._催促_60s_played = True
    
    def switch_player(self, new_player):
        """切换玩家 - 只处理AI思考语音，不处理时间统计"""
        print(f"switch_player被调用: 切换到 {new_player}")
        
        # AI思考语音逻辑 - AI回合开始时触发
        if (new_player == PLAYER_BLACK and  # 假设AI是黑棋时触发
            self.move_count > 18 and        # 总回合大于18
            random.random() < 0.3):         # 30%概率触发

            if self._play_voice("思考"):
                print(f"AI回合开始，播放思考语音（总回合：{self.move_count}）")
    
    def add_move(self, row, col, player):
        """添加移动记录 - 不处理时间统计"""
        # 添加移动记录
        self.move_history.append((row, col, player))
        self.move_count += 1
        
        print(f"添加移动: ({row}, {col}), 玩家: {player}，总步数: {self.move_count}")
    
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
        current_time = time.time()
        
        # 计算当前玩家的实时用时
        current_player_time = current_time - self.current_player_start_time
        
        # 计算总用时（包括当前玩家正在进行的时间）
        total_black_time = self.player_black_total_time
        total_white_time = self.player_white_total_time
        
        if self.last_player == PLAYER_BLACK:
            total_black_time += current_player_time
        elif self.last_player == PLAYER_WHITE:
            total_white_time += current_player_time
        
        game_duration = current_time - self.game_start_time
        
        return {
            'game_duration': game_duration,
            'move_count': self.move_count,
            'black_time': total_black_time,
            'white_time': total_white_time,
            'undo_count': self.undo_count
        }
    
    def get_final_statistics(self):
        """获取最终统计信息"""
        game_duration = time.time() - self.game_start_time
        
        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        
        stats = f" Game Statistics \n"
        stats += f"Total Time: {format_time(game_duration)}\n"
        stats += f"Total Moves: {self.move_count}\n"
        stats += f"Black Time: {format_time(self.player_black_total_time)}\n"
        stats += f"White Time: {format_time(self.player_white_total_time)}\n"
        stats += f"Undos Used: {self.undo_count} times"
        
        return stats
    
    def play_undo_voice(self, ai_type=None):
        """播放悔棋语音 - 三次悔棋不重复播放"""
        if not self.audio_manager or not self._can_play_voice():
            print("悔棋语音被冷却限制，跳过播放")
            return False
        
        # 获取所有包含"悔棋"关键词的语音索引
        undo_voice_indices = self._get_undo_voice_indices(ai_type)
        
        if not undo_voice_indices:
            print("没有找到悔棋语音")
            return False
        
        # 选择未播放过的语音
        available_indices = [idx for idx in undo_voice_indices if idx not in self._undo_voice_played]
        
        if not available_indices:
            # 如果所有悔棋语音都播放过了，重置列表（理论上不会发生，因为最多3次悔棋）
            print("所有悔棋语音都已播放，重置播放记录")
            self._undo_voice_played = []
            available_indices = undo_voice_indices
        
        # 随机选择一个未播放过的悔棋语音
        selected_index = random.choice(available_indices)
        
        # 直接使用索引播放语音
        result = self.audio_manager.play_ai_voice(
            identifier=selected_index,  # 直接传递索引
            volume=1.0,
            ai_type=ai_type
        )
        
        if result:
            # 记录已播放的语音索引
            self._undo_voice_played.append(selected_index)
            self._last_voice_time = time.time()
            print(f"播放悔棋语音 (索引:{selected_index}), 已播放列表: {self._undo_voice_played}")
            return True
        else:
            print("悔棋语音播放失败")
            return False
    
    def _get_undo_voice_indices(self, ai_type=None):
        """获取所有悔棋语音的索引"""
        if not self.audio_manager:
            return []
        
        # 确定使用的AI类型和语音包
        target_ai_type = ai_type if ai_type else self.audio_manager.current_ai_type
        voice_pack = self.audio_manager.AI_VOICE_MAPPING.get(target_ai_type, "nahita")
        
        undo_indices = []
        
        if voice_pack == "nahita":
            # 在Nahita语音中查找包含"悔棋"的语音
            for keyword, index in self.audio_manager.nahita_voice_map.items():
                if "悔棋" in keyword:
                    undo_indices.append(index)
        elif voice_pack == "tinyun":
            # 在Tinyun语音中查找包含"悔棋"的语音
            for keyword, index in self.audio_manager.tinyun_voice_map.items():
                if "悔棋" in keyword:
                    undo_indices.append(index)
        
        print(f"找到 {len(undo_indices)} 个悔棋语音 ({voice_pack}): {undo_indices}")
        return undo_indices