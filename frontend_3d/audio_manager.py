"""音频管理模块"""
import os
import random
import time
from utils.constants import (
    BGM_LIST, SOUND_CLICK, SOUND_DRAG, WINNER_MUSIC, LOSER_MUSIC, SOUND_VOLUME
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