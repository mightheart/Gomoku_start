"""音频管理模块"""
import os
import random
import time
from utils.constants import (
    BGM_LIST, NAHITA_VOICE, TINYUN_VOICE, SOUND_CLICK, SOUND_DRAG, WINNER_MUSIC, LOSER_MUSIC, SOUND_VOLUME
)

class AudioManager:
    """音频管理器"""
    
    def __init__(self, loader, task_mgr):
        self.loader = loader
        self.task_mgr = task_mgr
        
        # 音效
        self.place_piece_sound = None
        self.drag_piece_sound = None
        self.winner_music = None
        self.loser_music = None
        
        # 背景音乐
        self.bgm_list = []
        self.current_bgm_index = 0
        self.current_bgm = None

        # Nahita语音
        self.nahita_voices = []
        self.nahita_voice_map = {}  # 用于关键词映射
        self.last_played_voice_index = -1  # 记录上次播放的语音索引
        
        # Tinyun语音
        self.tinyun_voices = []
        self.tinyun_voice_map = {}  # 用于关键词映射
        self.last_played_tinyun_voice_index = -1  # 记录上次播放的语音索引

        # 使用多种方式确保真正的随机性
        self._init_random_seed()
        
        self._load_all_audio()
    
    def _init_random_seed(self):
        """初始化随机种子，确保真正的随机性"""
        try:
            # 方法1：使用当前时间的微秒部分
            current_time = time.time()
            seed = int((current_time * 1000000) % 2**32)
            random.seed(seed)
            print(f"使用时间种子初始化随机数: {seed}")
            
            # 方法2：额外的随机化（混合多个时间源）
            import hashlib
            import os
            time_str = str(time.time()) + str(time.perf_counter()) + str(os.getpid())
            hash_seed = int(hashlib.md5(time_str.encode()).hexdigest()[:8], 16)
            random.seed(hash_seed)
            print(f"使用混合哈希种子: {hash_seed}")
            
        except Exception as e:
            print(f"随机种子初始化失败，使用默认: {e}")
            random.seed()
    
    def _get_random_choice(self, choices):
        """获取真正随机的选择"""
        if not choices:
            return None
        
        # 使用当前时间的微秒级精度作为额外随机源
        current_microseconds = int(time.time() * 1000000)
        
        # 结合系统时间和内置随机函数
        index = (current_microseconds + random.randint(0, 1000000)) % len(choices)
        return choices[index]
    
    def _load_all_audio(self):
        """加载所有音频文件"""
        try:
            # 加载音效
            self.place_piece_sound = self.loader.loadSfx(SOUND_CLICK)
            self.drag_piece_sound = self.loader.loadSfx(SOUND_DRAG)
            
            try:
                self.winner_music = self.loader.loadSfx(WINNER_MUSIC)
                self.loser_music = self.loader.loadSfx(LOSER_MUSIC)
            except:
                print("胜利/失败音效文件不存在，跳过加载")
                self.winner_music = None
                self.loser_music = None

            # 加载Nahita语音
            for i, voice_file in enumerate(NAHITA_VOICE):
                if os.path.exists(voice_file):
                    voice = self.loader.loadSfx(voice_file)
                    if voice:
                        self.nahita_voices.append(voice)
                        # 创建关键词映射，从文件名提取关键词
                        filename = os.path.basename(voice_file).replace('.wav', '')
                        self.nahita_voice_map[filename] = i
                        print(f"Nahita语音 {filename} 加载成功")
                else:
                    self.nahita_voices.append(None)
                    print(f"Nahita语音文件不存在: {voice_file}")

            # 加载Tinyun语音
            for i, voice_file in enumerate(TINYUN_VOICE):
                if os.path.exists(voice_file):
                    voice = self.loader.loadSfx(voice_file)
                    if voice:
                        self.tinyun_voices.append(voice)
                        # 创建关键词映射，从文件名提取关键词
                        filename = os.path.basename(voice_file).replace('.wav', '')
                        self.tinyun_voice_map[filename] = i
                        print(f"Tinyun语音 {filename} 加载成功")
                else:
                    self.tinyun_voices.append(None)
                    print(f"Tinyun语音文件不存在: {voice_file}")

            # 加载背景音乐
            for bgm_file in BGM_LIST:
                if os.path.exists(bgm_file):
                    bgm = self.loader.loadMusic(bgm_file)
                    if bgm:
                        self.bgm_list.append(bgm)
                        print(f"背景音乐 {bgm_file} 加载成功")
            
            # 开始播放背景音乐
            if self.bgm_list:
                self.current_bgm_index = random.randint(0, len(self.bgm_list) - 1)
                self.play_current_bgm()
                
        except Exception as e:
            print(f"音频加载失败: {e}")

    def play_nahita_voice(self, identifier=None, volume=None):
        """
        播放Nahita语音
        Args:
            identifier: 可以是以下几种类型：
                    - int: 索引值 (0-10)
                    - str: 关键词匹配 (如 "摸摸头", "初次见面")
                    - None: 随机播放
            volume: 音量 (0.0-1.0)，默认使用SOUND_VOLUME
        
        Returns:
            bool: 播放成功返回True，失败返回False
        """
        if not self.nahita_voices:
            print("没有可用的Nahita语音")
            return False
        
        # 每次播放前重新随机化（确保真正随机）
        random.seed(int(time.time() * 1000000) % 2**32)
        
        # 确定要播放的语音索引
        voice_index = None
        
        if identifier is None:
            # 随机播放 - 避免重复
            voice_index = self._get_random_voice_index()
        elif isinstance(identifier, int):
            # 按索引播放
            if 0 <= identifier < len(self.nahita_voices):
                voice_index = identifier
            else:
                print(f"语音索引超出范围: {identifier}")
                return False
        elif isinstance(identifier, str):
            # 按关键词匹配 - 找到所有匹配项，然后随机选择一个（避免重复）
            voice_index = self._get_matched_voice_index(identifier)
        
        # 播放语音
        if voice_index is not None and voice_index < len(self.nahita_voices) and self.nahita_voices[voice_index] is not None:
            voice = self.nahita_voices[voice_index]
            voice.setVolume(volume if volume is not None else SOUND_VOLUME)
            voice.play()
            
            # 记录这次播放的索引
            self.last_played_voice_index = voice_index
            
            # 获取文件名用于日志
            filename = os.path.basename(NAHITA_VOICE[voice_index]).replace('.wav', '')
            print(f"播放Nahita语音: {filename} (索引: {voice_index})")
            return True
        else:
            print(f"语音文件不可用: 索引 {voice_index}")
            return False

    def play_tinyun_voice(self, identifier=None, volume=None):
        """
        播放Tinyun语音
        Args:
            identifier: 可以是以下几种类型：
                    - int: 索引值 (0-25)
                    - str: 关键词匹配 (如 "催促", "欢迎", "思考")
                    - None: 随机播放
            volume: 音量 (0.0-1.0)，默认使用SOUND_VOLUME
        
        Returns:
            bool: 播放成功返回True，失败返回False
        """
        if not self.tinyun_voices:
            print("没有可用的Tinyun语音")
            return False
        
        # 每次播放前重新随机化（确保真正随机）
        random.seed(int(time.time() * 1000000) % 2**32)
        
        # 确定要播放的语音索引
        voice_index = None
        
        if identifier is None:
            # 随机播放 - 避免重复
            voice_index = self._get_random_tinyun_voice_index()  # 应该调用Tinyun专用函数
        elif isinstance(identifier, int):
            # 按索引播放
            if 0 <= identifier < len(self.tinyun_voices):
                voice_index = identifier
            else:
                print(f"Tinyun语音索引超出范围: {identifier}")
                return False
        elif isinstance(identifier, str):
            # 按关键词匹配 - 找到所有匹配项，然后随机选择一个（避免重复）
            voice_index = self._get_matched_tinyun_voice_index(identifier)  # 应该调用Tinyun专用函数
        
        # 播放语音
        if voice_index is not None and voice_index < len(self.tinyun_voices) and self.tinyun_voices[voice_index] is not None:
            voice = self.tinyun_voices[voice_index]
            voice.setVolume(volume if volume is not None else SOUND_VOLUME)
            voice.play()
            
            # 记录这次播放的索引
            self.last_played_tinyun_voice_index = voice_index
            
            # 获取文件名用于日志
            filename = os.path.basename(TINYUN_VOICE[voice_index]).replace('.wav', '')
            print(f"播放Tinyun语音: {filename} (索引: {voice_index})")
            return True
        else:
            print(f"Tinyun语音文件不可用: 索引 {voice_index}")
            return False

    def _get_random_voice_index(self):
        """获取随机语音索引，避免与上次重复"""
        valid_indices = [i for i, voice in enumerate(self.nahita_voices) if voice is not None]
        
        if not valid_indices:
            return None
        
        if len(valid_indices) == 1:
            # 只有一个可用语音，直接返回
            return valid_indices[0]
        
        # 如果有多个可用语音，避免重复
        if self.last_played_voice_index in valid_indices:
            # 移除上次播放的索引
            available_indices = [i for i in valid_indices if i != self.last_played_voice_index]
            if available_indices:
                return self._get_random_choice(available_indices)
        
        # 如果上次播放的不在有效列表中，或者没有其他选择，随机选择
        return self._get_random_choice(valid_indices)
    
    def _get_matched_voice_index(self, identifier):
        """获取匹配关键词的语音索引，避免重复"""
        matched_indices = []
        for keyword, index in self.nahita_voice_map.items():
            if identifier in keyword and index < len(self.nahita_voices) and self.nahita_voices[index] is not None:
                matched_indices.append(index)
        
        if not matched_indices:
            print(f"未找到匹配关键词的语音: {identifier}")
            return None
        
        if len(matched_indices) == 1:
            # 只有一个匹配，直接返回
            print(f"关键词 '{identifier}' 匹配到 1 个语音")
            return matched_indices[0]
        
        # 多个匹配时避免重复
        if self.last_played_voice_index in matched_indices:
            # 移除上次播放的索引
            available_indices = [i for i in matched_indices if i != self.last_played_voice_index]
            if available_indices:
                selected_index = self._get_random_choice(available_indices)
                print(f"关键词 '{identifier}' 匹配到 {len(matched_indices)} 个语音，避免重复后随机选择")
                return selected_index
        
        # 如果上次播放的不在匹配列表中，随机选择
        selected_index = self._get_random_choice(matched_indices)
        print(f"关键词 '{identifier}' 匹配到 {len(matched_indices)} 个语音，随机选择")
        return selected_index

    def _get_random_tinyun_voice_index(self):
        """获取随机Tinyun语音索引，避免与上次重复"""
        valid_indices = [i for i, voice in enumerate(self.tinyun_voices) if voice is not None]
        
        if not valid_indices:
            return None
        
        if len(valid_indices) == 1:
            # 只有一个可用语音，直接返回
            return valid_indices[0]
        
        # 如果有多个可用语音，避免重复
        if self.last_played_tinyun_voice_index in valid_indices:
            # 移除上次播放的索引
            available_indices = [i for i in valid_indices if i != self.last_played_tinyun_voice_index]
            if available_indices:
                return self._get_random_choice(available_indices)
        
        # 如果上次播放的不在有效列表中，或者没有其他选择，随机选择
        return self._get_random_choice(valid_indices)

    def _get_matched_tinyun_voice_index(self, identifier):
        """获取匹配关键词的Tinyun语音索引，避免重复"""
        matched_indices = []
        for keyword, index in self.tinyun_voice_map.items():  # 使用tinyun_voice_map
            if identifier in keyword and index < len(self.tinyun_voices) and self.tinyun_voices[index] is not None:
                matched_indices.append(index)
        
        if not matched_indices:
            print(f"未找到匹配关键词的Tinyun语音: {identifier}")
            return None
        
        if len(matched_indices) == 1:
            # 只有一个匹配，直接返回
            print(f"关键词 '{identifier}' 匹配到 1 个Tinyun语音")
            return matched_indices[0]
        
        # 多个匹配时避免重复
        if self.last_played_tinyun_voice_index in matched_indices:
            # 移除上次播放的索引
            available_indices = [i for i in matched_indices if i != self.last_played_tinyun_voice_index]
            if available_indices:
                selected_index = self._get_random_choice(available_indices)
                print(f"关键词 '{identifier}' 匹配到 {len(matched_indices)} 个Tinyun语音，避免重复后随机选择")
                return selected_index
        
        # 如果上次播放的不在匹配列表中，随机选择
        selected_index = self._get_random_choice(matched_indices)
        print(f"关键词 '{identifier}' 匹配到 {len(matched_indices)} 个Tinyun语音，随机选择")
        return selected_index

    def get_tinyun_voice_list(self):
        """获取可用的Tinyun语音列表"""
        voice_list = []
        for i, voice_file in enumerate(TINYUN_VOICE):
            filename = os.path.basename(voice_file).replace('.wav', '')
            available = self.tinyun_voices[i] is not None if i < len(self.tinyun_voices) else False
            voice_list.append({
                'index': i,
                'filename': filename,
                'path': voice_file,
                'available': available
            })
        return voice_list

    def play_place_piece_sound(self):
        """播放下棋音效"""
        if self.place_piece_sound:
            self.place_piece_sound.setVolume(SOUND_VOLUME)
            self.place_piece_sound.play()
    
    def play_drag_piece_sound(self):
        """播放提子音效"""
        if self.drag_piece_sound:
            self.drag_piece_sound.setVolume(SOUND_VOLUME)
            self.drag_piece_sound.play()
    
    def play_winner_sound(self):
        """播放胜利音效并暂停背景音乐"""
        self.stop_all_music()  # 停止所有音乐
        if self.winner_music:
            self.winner_music.setVolume(SOUND_VOLUME*0.1)
            self.winner_music.play()
    
    def play_loser_sound(self):
        """播放失败音效并暂停背景音乐"""
        self.stop_all_music()  # 停止所有音乐
        if self.loser_music:
            self.loser_music.setVolume(SOUND_VOLUME-0.1)
            self.loser_music.play()
    
    def play_current_bgm(self):
        """播放当前背景音乐"""
        self.task_mgr.remove('bgm-switch-task')
        if self.bgm_list and 0 <= self.current_bgm_index < len(self.bgm_list):
            if self.current_bgm:
                self.current_bgm.stop()
            
            self.current_bgm = self.bgm_list[self.current_bgm_index]
            self.current_bgm.setVolume(SOUND_VOLUME)
            self.current_bgm.play()
            
            try:
                duration = self.current_bgm.length()
                if duration > 0:
                    self.task_mgr.doMethodLater(duration, self._switch_to_next_bgm, 'bgm-switch-task')
                else:
                    self.task_mgr.doMethodLater(180, self._switch_to_next_bgm, 'bgm-switch-task')
            except:
                self.task_mgr.doMethodLater(180, self._switch_to_next_bgm, 'bgm-switch-task')
    
    def _switch_to_next_bgm(self, task):
        """切换到下一首背景音乐"""
        if self.bgm_list:
            self.current_bgm_index = (self.current_bgm_index + 1) % len(self.bgm_list)
            self.play_current_bgm()
        return task.done
    
    def stop_bgm(self):
        """停止背景音乐"""
        if self.current_bgm:
            self.current_bgm.stop()
    
    def stop_all_music(self):
        """停止所有音乐，包括背景音乐和胜利/失败音乐"""
        #移除旧的切歌任务
        self.task_mgr.remove('bgm-switch-task')
        if self.current_bgm:
            self.current_bgm.stop()
        if self.winner_music:
            self.winner_music.stop()
        if self.loser_music:
            self.loser_music.stop()