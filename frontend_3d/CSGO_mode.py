from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Vec3
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from frontend_3d.setup_scene import SceneSetup
from frontend_3d.setup_board import BoardSetup
from frontend_3d.audio_manager import AudioManager
import sys

class CSGOCameraDemo:
    def __init__(self, base):
        self.base = base
        for attr in dir(base):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(base, attr))

        self._setup_window()
        self._setup_camera()
        self._init_audio()
        self._init_scene()
        self._init_board()
        self._init_controls()
        self._init_ui()
        self._start_tasks()
        self._welcome_voice_played = False  # 欢迎语音，只播放一次

    def _setup_window(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)

    def _setup_camera(self):
        self.disableMouse()
        self.camera.setPos(0, -35, 5)
        self.pitch = 0
        self.yaw = 0

    def _init_audio(self):
        self.audio_manager = AudioManager(self.loader, self.taskMgr)

    def _init_scene(self):
        self.scene_setup = SceneSetup(self.loader, self.render, self.taskMgr)
        self.scene_setup.setup_lighting()
        self.scene_setup.load_scene()
        self.ground = self.scene_setup.ground_model

    def _init_board(self):
        self.board_setup = BoardSetup(self.loader, self.render)
        self.board_setup.setup_board()

    def _init_controls(self):
        self.mouse_sensitivity = 0.05
        self.move_speed = 0.6
        self.key_map = {"w": False, "s": False, "a": False, "d": False}
        for key in self.key_map:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", sys.exit)

    

    def _init_ui(self):
        self.cam_pos_text = OnscreenText(
            text="",
            pos=(-1.3, 0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=0,
            parent=self.aspect2d
        )
        self.in_gomoku_area = False
        self.hint_text = None

    def _start_tasks(self):
        self.taskMgr.add(self.update_camera, "UpdateCameraTask")
        self.last_mouse_pos = None
        self.taskMgr.add(self.check_gomoku_area, "CheckGomokuArea")

    def set_key(self, key, value):
        self.key_map[key] = value

    def update_camera(self, task):
        # 鼠标视角
        if self.base.mouseWatcherNode.hasMouse():
            x = self.base.win.getPointer(0).getX()
            y = self.base.win.getPointer(0).getY()
            win_cx = self.base.win.getXSize() // 2
            win_cy = self.base.win.getYSize() // 2
            if self.last_mouse_pos is not None:
                dx = x - win_cx
                dy = y - win_cy
                self.yaw -= dx * self.mouse_sensitivity
                self.pitch -= dy * self.mouse_sensitivity
                self.pitch = max(-89, min(89, self.pitch))
                self.base.camera.setHpr(self.yaw, self.pitch, 0)
            self.base.win.movePointer(0, win_cx, win_cy)
            self.last_mouse_pos = (win_cx, win_cy)

        # 键盘移动
        dir_vec = Vec3(0, 0, 0)
        quat = self.base.camera.getQuat()
        if self.key_map["w"]:
            dir_vec += quat.getForward()
        if self.key_map["s"]:
            dir_vec -= quat.getForward()
        if self.key_map["a"]:
            dir_vec -= quat.getRight()
        if self.key_map["d"]:
            dir_vec += quat.getRight()
        dir_vec.setZ(0)
        if dir_vec.length() > 0:
            dir_vec.normalize()
            self.base.camera.setPos(self.base.camera.getPos() + dir_vec * self.move_speed)

        # 实时更新摄像机位置文本
        pos = self.base.camera.getPos()

        # 限制摄像机坐标
        x = max(-60, min(60, pos.x))
        y = max(-900, min(85.27, pos.y))
        z = 5  # 固定高度
        self.base.camera.setPos(x, y, z)

        self.cam_pos_text.setText(f"Pos: ({x:.2f}, {y:.2f}, {z:.2f})")
        return Task.cont

    def check_gomoku_area(self, task):
        cam_pos = self.base.camera.getPos()
        from panda3d.core import Vec3
        gomoku_center = Vec3(0, 0, 0)
        radius = 20
        if (cam_pos - gomoku_center).length() < radius:
            if not self.in_gomoku_area:
                self.in_gomoku_area = True
                self.hint_text = OnscreenText("Press space to enter the game", pos=(0, 0.8), scale=0.1, fg=(1,1,0,1), parent=self.base.aspect2d)
                self.base.accept("space", self._start_gomoku)
                
                # 首次触发时播放欢迎语音
                if not self._welcome_voice_played:
                    self._play_welcome_voice()
                    self._welcome_voice_played = True
        else:
            if self.in_gomoku_area:
                self.in_gomoku_area = False
                if self.hint_text:
                    self.hint_text.destroy()
                    self.hint_text = None
                self.base.ignore("space")
        return Task.cont

    def _start_gomoku(self):
        # 通知主程序切换到Gomoku模式
        if hasattr(self.base, "messenger"):
            self.base.messenger.send("start-gomoku", [self.base.camera.getPos(), self.base.camera.getHpr()])

    def _play_welcome_voice(self):
        """播放欢迎语音"""
        if hasattr(self, 'audio_manager') and self.audio_manager:
            print("播放首次接近棋盘的欢迎语音")
            result = self.audio_manager.play_nahita_voice("欢迎", volume=1)
            print(f"欢迎语音播放结果: {result}")

    def cleanup(self):
        # 清理UI、任务、模型、墙体、音乐等
        if self.hint_text:
            self.hint_text.destroy()
        self.base.taskMgr.remove("CheckGomokuArea")
        self.base.taskMgr.remove("UpdateCameraTask")
        self.cam_pos_text.destroy()
        if hasattr(self, "scene_setup"):
            self.scene_setup.cleanup()
        if hasattr(self, "board_setup"):
            self.board_setup.cleanup()
        if hasattr(self, "wall_nodes"):
            for node in self.wall_nodes:
                node.removeNode()
            self.wall_nodes.clear()
        # 清理音乐
        if hasattr(self, "audio_manager"):
            self.audio_manager.stop_all_music()
        # 重置欢迎语音标记（重新进入CSGO模式时可以再次播放）
        self._welcome_voice_played = False

    def restore_camera(self, pos, hpr):
        self.base.camera.setPos(pos)
        self.base.camera.setHpr(hpr)