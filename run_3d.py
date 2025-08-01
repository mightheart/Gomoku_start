#!/usr/bin/env python
"""
Run Gomoku game.
"""

from direct.showbase.ShowBase import ShowBase
from frontend_3d.CSGO_mode import CSGOCameraDemo
from frontend_3d.game import Gomoku_Start

class MainApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.mode = "csgo"
        self.csgo_mode = CSGOCameraDemo(self)
        self.gomoku_mode = None
        self.last_camera_pos = None
        self.last_camera_hpr = None

        # 监听切换事件
        self.accept("start-gomoku", self.start_gomoku)
        self.accept("back-to-csgo", self.back_to_csgo)

    def start_gomoku(self, camera_pos, camera_hpr, ai_type="classical", board_y=0, opponent_model_path=None, opponent_model_position=None):
        self.last_camera_pos = camera_pos
        self.last_camera_hpr = camera_hpr
        if self.gomoku_mode:
            self.gomoku_mode.cleanup()
            self.gomoku_mode = None
        if self.csgo_mode:
            self.csgo_mode.cleanup()
            self.csgo_mode = None

        self.gomoku_mode = Gomoku_Start(
            self,
            ai_type=ai_type,
            board_y=board_y,
            opponent_model_path=opponent_model_path,
            opponent_model_position=opponent_model_position
        )
        self.mode = "gomoku"

    def back_to_csgo(self):
        # 清理Gomoku模式
        if self.gomoku_mode:
            self.gomoku_mode.cleanup()
            self.gomoku_mode = None
        # 清理旧的 csgo_mode
        if self.csgo_mode:
            self.csgo_mode.cleanup()
            self.csgo_mode = None
        # 恢复CSGO模式
        self.csgo_mode = CSGOCameraDemo(self)
        if self.last_camera_pos:
            self.csgo_mode.camera.setPos(self.last_camera_pos)
            self.csgo_mode.camera.setHpr(self.last_camera_hpr)
        self.mode = "csgo"

if __name__ == "__main__":
    app = MainApp()
    app.run()