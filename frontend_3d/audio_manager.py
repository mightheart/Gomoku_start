"""音频管理模块"""
import os
import random
import time
from utils.constants import (
    BGM_LIST, NAHITA_VOICE, SOUND_CLICK, SOUND_DRAG, WINNER_MUSIC, LOSER_MUSIC, SOUND_VOLUME
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
        
        self._load_all_audio()
    
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
        
        # 确定要播放的语音索引
        voice_index = None
        
        if identifier is None:
            # 随机播放
            valid_indices = [i for i, voice in enumerate(self.nahita_voices) if voice is not None]
            if valid_indices:
                voice_index = random.choice(valid_indices)
        elif isinstance(identifier, int):
            # 按索引播放
            if 0 <= identifier < len(self.nahita_voices):
                voice_index = identifier
            else:
                print(f"语音索引超出范围: {identifier}")
                return False
        elif isinstance(identifier, str):
            # 按关键词匹配 - 找到所有匹配项，然后随机选择一个
            matched_indices = []
            for keyword, index in self.nahita_voice_map.items():
                if identifier in keyword:
                    matched_indices.append(index)
            
            if matched_indices:
                voice_index = random.choice(matched_indices)
                print(f"关键词 '{identifier}' 匹配到 {len(matched_indices)} 个语音，随机选择播放")
            else:
                print(f"未找到匹配关键词的语音: {identifier}")
                return False
        
        # 播放语音
        if voice_index is not None and voice_index < len(self.nahita_voices) and self.nahita_voices[voice_index] is not None:
            voice = self.nahita_voices[voice_index]
            voice.setVolume(volume if volume is not None else SOUND_VOLUME)
            voice.play()
            
            # 获取文件名用于日志
            filename = os.path.basename(NAHITA_VOICE[voice_index]).replace('.wav', '')
            print(f"播放Nahita语音: {filename}")
            return True
        else:
            print(f"语音文件不可用: 索引 {voice_index}")
            return False
    
    def get_nahita_voice_list(self):
        """获取可用的Nahita语音列表"""
        voice_list = []
        for i, voice_file in enumerate(NAHITA_VOICE):
            filename = os.path.basename(voice_file).replace('.wav', '')
            available = self.nahita_voices[i] is not None if i < len(self.nahita_voices) else False
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
            self.winner_music.setVolume(SOUND_VOLUME)
            self.winner_music.play()
    
    def play_loser_sound(self):
        """播放失败音效并暂停背景音乐"""
        self.stop_all_music()  # 停止所有音乐
        if self.loser_music:
            self.loser_music.setVolume(SOUND_VOLUME)
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