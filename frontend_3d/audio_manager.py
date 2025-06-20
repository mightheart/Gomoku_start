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
        
        # 当前AI类型，决定使用哪套语音
        self.current_ai_type = "classical"  # 默认classical
        
        # 音效
        self.place_piece_sound = None
        self.drag_piece_sound = None
        self.winner_music = None
        self.loser_music = None
        
        # 背景音乐
        self.bgm_list = []
        self.current_bgm_index = 0
        self.current_bgm = None

        # Nahita语音 (classical AI)
        self.nahita_voices = []
        self.nahita_voice_map = {}
        self.last_played_nahita_index = -1
        
        # Tinyun语音 (minimax & mcts AI)
        self.tinyun_voices = []
        self.tinyun_voice_map = {}
        self.last_played_tinyun_index = -1

        # AI类型与语音包映射
        self.AI_VOICE_MAPPING = {
            "classical": "nahita",
            "minimax": "tinyun", 
            "mcts": "tinyun"
        }

        self._init_random_seed()
        self._load_all_audio()
    
    def set_ai_type(self, ai_type):
        """设置当前AI类型，用于确定语音包"""
        if ai_type in self.AI_VOICE_MAPPING:
            self.current_ai_type = ai_type
            voice_pack = self.AI_VOICE_MAPPING[ai_type]
            print(f"设置AI类型: {ai_type}, 使用语音包: {voice_pack}")
        else:
            print(f"未知AI类型: {ai_type}, 使用默认classical")
            self.current_ai_type = "classical"
    
    def play_ai_voice(self, identifier=None, volume=None, ai_type=None):
        """
        统一的AI语音播放函数
        Args:
            identifier: 语音标识符 (int索引 / str关键词 / None随机)
            volume: 音量 (0.0-1.0)
            ai_type: 指定AI类型 (可选，不指定则使用当前设置的类型)
        
        Returns:
            bool: 播放成功返回True，失败返回False
        """
        # 确定使用的AI类型
        target_ai_type = ai_type if ai_type else self.current_ai_type
        voice_pack = self.AI_VOICE_MAPPING.get(target_ai_type, "nahita")
        
        print(f"播放AI语音 - AI类型: {target_ai_type}, 语音包: {voice_pack}, 标识符: {identifier}")
        
        # 根据语音包调用对应的播放函数
        if voice_pack == "nahita":
            return self._play_nahita_voice_internal(identifier, volume)
        elif voice_pack == "tinyun":
            return self._play_tinyun_voice_internal(identifier, volume)
        else:
            print(f"未知语音包: {voice_pack}")
            return False
    
    def _play_nahita_voice_internal(self, identifier=None, volume=None):
        """内部Nahita语音播放函数"""
        if not self.nahita_voices:
            print("没有可用的Nahita语音")
            return False
        
        random.seed(int(time.time() * 1000000) % 2**32)
        
        voice_index = None
        if identifier is None:
            voice_index = self._get_random_nahita_voice_index()
        elif isinstance(identifier, int):
            if 0 <= identifier < len(self.nahita_voices):
                voice_index = identifier
            else:
                print(f"Nahita语音索引超出范围: {identifier}")
                return False
        elif isinstance(identifier, str):
            voice_index = self._get_matched_nahita_voice_index(identifier)
        
        if voice_index is not None and voice_index < len(self.nahita_voices) and self.nahita_voices[voice_index] is not None:
            voice = self.nahita_voices[voice_index]
            voice.setVolume(volume if volume is not None else SOUND_VOLUME)
            voice.play()
            
            self.last_played_nahita_index = voice_index
            filename = os.path.basename(NAHITA_VOICE[voice_index]).replace('.wav', '')
            print(f"播放Nahita语音: {filename} (索引: {voice_index})")
            return True
        else:
            print(f"Nahita语音文件不可用: 索引 {voice_index}")
            return False
    
    def _play_tinyun_voice_internal(self, identifier=None, volume=None):
        """内部Tinyun语音播放函数"""
        if not self.tinyun_voices:
            print("没有可用的Tinyun语音")
            return False
        
        random.seed(int(time.time() * 1000000) % 2**32)
        
        voice_index = None
        if identifier is None:
            voice_index = self._get_random_tinyun_voice_index()
        elif isinstance(identifier, int):
            if 0 <= identifier < len(self.tinyun_voices):
                voice_index = identifier
            else:
                print(f"Tinyun语音索引超出范围: {identifier}")
                return False
        elif isinstance(identifier, str):
            voice_index = self._get_matched_tinyun_voice_index(identifier)
        
        if voice_index is not None and voice_index < len(self.tinyun_voices) and self.tinyun_voices[voice_index] is not None:
            voice = self.tinyun_voices[voice_index]
            voice.setVolume(volume if volume is not None else SOUND_VOLUME)
            voice.play()
            
            self.last_played_tinyun_index = voice_index
            filename = os.path.basename(TINYUN_VOICE[voice_index]).replace('.wav', '')
            print(f"播放Tinyun语音: {filename} (索引: {voice_index})")
            return True
        else:
            print(f"Tinyun语音文件不可用: 索引 {voice_index}")
            return False
    
    def _get_random_nahita_voice_index(self):
        """获取随机Nahita语音索引"""
        valid_indices = [i for i, voice in enumerate(self.nahita_voices) if voice is not None]
        if not valid_indices:
            return None
        if len(valid_indices) == 1:
            return valid_indices[0]
        if self.last_played_nahita_index in valid_indices:
            available_indices = [i for i in valid_indices if i != self.last_played_nahita_index]
            if available_indices:
                return self._get_random_choice(available_indices)
        return self._get_random_choice(valid_indices)
    
    def _get_matched_nahita_voice_index(self, identifier):
        """获取匹配关键词的Nahita语音索引"""
        matched_indices = []
        for keyword, index in self.nahita_voice_map.items():
            if identifier in keyword and index < len(self.nahita_voices) and self.nahita_voices[index] is not None:
                matched_indices.append(index)
        
        if not matched_indices:
            print(f"未找到匹配关键词的Nahita语音: {identifier}")
            return None
        if len(matched_indices) == 1:
            return matched_indices[0]
        if self.last_played_nahita_index in matched_indices:
            available_indices = [i for i in matched_indices if i != self.last_played_nahita_index]
            if available_indices:
                return self._get_random_choice(available_indices)
        return self._get_random_choice(matched_indices)
    
    def play_nahita_voice(self, identifier=None, volume=None):
        """兼容性接口 - 直接播放Nahita语音"""
        return self._play_nahita_voice_internal(identifier, volume)
    
    def _get_random_tinyun_voice_index(self):
        """获取随机Tinyun语音索引，避免与上次重复"""
        valid_indices = [i for i, voice in enumerate(self.tinyun_voices) if voice is not None]
        
        if not valid_indices:
            return None
        
        if len(valid_indices) == 1:
            # 只有一个可用语音，直接返回
            return valid_indices[0]
        
        # 如果有多个可用语音，避免重复
        if self.last_played_tinyun_index in valid_indices:
            # 移除上次播放的索引
            available_indices = [i for i in valid_indices if i != self.last_played_tinyun_index]
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
        if self.last_played_tinyun_index in matched_indices:
            # 移除上次播放的索引
            available_indices = [i for i in matched_indices if i != self.last_played_tinyun_index]
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
    
    def _init_random_seed(self):
        """初始化随机种子"""
        random.seed(int(time.time() * 1000000) % 2**32)
    
    def _load_all_audio(self):
        """加载所有音频文件"""
        try:
            # 加载音效
            if os.path.exists(SOUND_CLICK):
                self.place_piece_sound = self.loader.loadSfx(SOUND_CLICK)
            
            if os.path.exists(SOUND_DRAG):
                self.drag_piece_sound = self.loader.loadSfx(SOUND_DRAG)
            
            if os.path.exists(WINNER_MUSIC):
                self.winner_music = self.loader.loadMusic(WINNER_MUSIC)
            
            if os.path.exists(LOSER_MUSIC):
                self.loser_music = self.loader.loadMusic(LOSER_MUSIC)
            
            # 加载背景音乐
            self._load_bgm()
            
            # 加载Nahita语音
            self._load_nahita_voices()
            
            # 加载Tinyun语音
            self._load_tinyun_voices()
            
        except Exception as e:
            print(f"加载音频文件时出错: {e}")
    
    def _load_bgm(self):
        """加载背景音乐"""
        for bgm_path in BGM_LIST:
            if os.path.exists(bgm_path):
                try:
                    bgm = self.loader.loadMusic(bgm_path)
                    if bgm:
                        self.bgm_list.append(bgm)
                except Exception as e:
                    print(f"加载背景音乐失败: {bgm_path}, 错误: {e}")
    
    def _load_nahita_voices(self):
        """加载Nahita语音文件"""
        self.nahita_voices = []
        self.nahita_voice_map = {}
        
        for i, voice_path in enumerate(NAHITA_VOICE):
            if os.path.exists(voice_path):
                try:
                    voice = self.loader.loadSfx(voice_path)
                    self.nahita_voices.append(voice)
                    
                    # 建立关键词映射
                    filename = os.path.basename(voice_path).replace('.wav', '')
                    self.nahita_voice_map[filename] = i
                    
                except Exception as e:
                    print(f"加载Nahita语音失败: {voice_path}, 错误: {e}")
                    self.nahita_voices.append(None)
            else:
                print(f"Nahita语音文件不存在: {voice_path}")
                self.nahita_voices.append(None)
    
    def _load_tinyun_voices(self):
        """加载Tinyun语音文件"""
        self.tinyun_voices = []
        self.tinyun_voice_map = {}
        
        for i, voice_path in enumerate(TINYUN_VOICE):
            if os.path.exists(voice_path):
                try:
                    voice = self.loader.loadSfx(voice_path)
                    self.tinyun_voices.append(voice)
                    
                    # 建立关键词映射
                    filename = os.path.basename(voice_path).replace('.wav', '')
                    self.tinyun_voice_map[filename] = i
                    
                except Exception as e:
                    print(f"加载Tinyun语音失败: {voice_path}, 错误: {e}")
                    self.tinyun_voices.append(None)
            else:
                print(f"Tinyun语音文件不存在: {voice_path}")
                self.tinyun_voices.append(None)
    
    def _get_random_choice(self, choices):
        """获取随机选择"""
        if not choices:
            return None
        return random.choice(choices)