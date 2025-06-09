"""输入管理模块"""
import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from utils.constants import UI_COLOR_YELLOW

class InputManager:
    """输入管理器"""
    
    def __init__(self, base_instance, camera_controller):
        self.base = base_instance
        self.camera_controller = camera_controller
        
        # 三连击检测
        self.key_press_times = {}
        self.key_press_counts = {}
        self.triple_click_threshold = 0.5
        self.auto_rotate_active = {}
        self.auto_rotate_task = None
        
        self._setup_input_bindings()
    
    def _setup_input_bindings(self):
        """设置输入绑定"""
        # 基本控制
        import sys
        self.base.accept('escape', sys.exit)
        
        # 摄像机控制
        self.base.accept("a", self._handle_key_press, ["cam-left"])
        self.base.accept("a-up", self._set_camera_key, ["cam-left", False])
        self.base.accept("d", self._handle_key_press, ["cam-right"])
        self.base.accept("d-up", self._set_camera_key, ["cam-right", False])
        self.base.accept("w", self._handle_key_press, ["cam-up"])
        self.base.accept("w-up", self._set_camera_key, ["cam-up", False])
        self.base.accept("s", self._handle_key_press, ["cam-down"])
        self.base.accept("s-up", self._set_camera_key, ["cam-down", False])
        
        # 游戏控制 - 修复方法名
        self.base.accept("u", self._handle_undo)
        self.base.accept("r", self._handle_restart)
        self.base.accept("tab", self._handle_tab)
        self.base.accept("space", self._stop_auto_rotate)
        
        # 鼠标控制
        self.base.accept("mouse1", lambda: self.base.mouse_picker.grab_piece())
        self.base.accept("mouse1-up", lambda: self.base.mouse_picker.release_piece())
        self.base.accept("wheel_up", self._zoom_in)
        self.base.accept("wheel_down", self._zoom_out)
    
    def _handle_undo(self):
        """处理悔棋"""
        self.base.undo_move()
    
    def _handle_restart(self):
        """处理重新开始"""
        self.base.restart_game()
    
    def _handle_tab(self):
        """处理Tab键"""
        self.base.ui_manager.toggle_ui_visibility()
    
    def _handle_key_press(self, key):
        """处理按键，检测三连击"""
        current_time = time.time()
        
        if key not in self.key_press_times:
            self.key_press_times[key] = []
            self.auto_rotate_active[key] = False
        
        # 清理过期记录
        self.key_press_times[key] = [t for t in self.key_press_times[key] 
                                    if current_time - t <= self.triple_click_threshold]
        
        self.key_press_times[key].append(current_time)
        
        # 检测三连击
        if len(self.key_press_times[key]) >= 3:
            recent_times = self.key_press_times[key][-3:]
            if recent_times[-1] - recent_times[0] <= self.triple_click_threshold:
                print(f"检测到 {key} 三连击！开始自动旋转")
                self._start_auto_rotate(key)
                self.key_press_times[key] = []
                return
        
        self._set_camera_key(key, True)
    
    def _start_auto_rotate(self, direction):
        """开始自动旋转"""
        self._stop_auto_rotate()
        
        for key in self.auto_rotate_active:
            self.auto_rotate_active[key] = False
        self.auto_rotate_active[direction] = True
        
        self.auto_rotate_task = self.base.taskMgr.add(self._auto_rotate_task, 'autoRotateTask')
        
        direction_text = {
            'cam-left': 'Rotating Clockwise',
            'cam-right': 'Rotating Anti-Clockwise', 
            'cam-up': 'Rotating Upward',
            'cam-down': 'Rotating Downward'
        }
        
        if hasattr(self, 'auto_rotate_hint'):
            self.auto_rotate_hint.destroy()
        
        self.auto_rotate_hint = OnscreenText(
            text=f"{direction_text.get(direction, 'Rotating')}... (Press Space To Stop)",
            parent=self.base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=UI_COLOR_YELLOW, pos=(0.8, -0.2), scale=.05)
    
    def _stop_auto_rotate(self):
        """停止自动旋转"""
        if self.auto_rotate_task:
            self.base.taskMgr.remove(self.auto_rotate_task)
            self.auto_rotate_task = None
        
        for key in self.auto_rotate_active:
            self.auto_rotate_active[key] = False
        
        # 停止所有摄像机键状态
        for direction in ['cam-left', 'cam-right', 'cam-up', 'cam-down']:
            self.camera_controller.set_key(direction, False)
        
        if hasattr(self, 'auto_rotate_hint'):
            self.auto_rotate_hint.destroy()
            delattr(self, 'auto_rotate_hint')
    
    def _auto_rotate_task(self, task):
        """自动旋转任务"""
        for direction, active in self.auto_rotate_active.items():
            self.camera_controller.set_key(direction, active)
        return task.cont
    
    def _set_camera_key(self, key, value):
        """设置摄像机键状态"""
        self.camera_controller.set_key(key, value)
    
    def _zoom_in(self):
        """放大视角"""
        current_fov = self.base.camLens.getFov()[0]
        new_fov = max(10, current_fov - 5)
        self.base.camLens.setFov(new_fov)
    
    def _zoom_out(self):
        """缩小视角"""
        current_fov = self.base.camLens.getFov()[0]
        new_fov = min(120, current_fov + 5)
        self.base.camLens.setFov(new_fov)