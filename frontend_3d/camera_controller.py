"""摄像机控制模块"""

import math
import builtins
from utils.constants import CAMERA_ROTATION_SPEED, CAMERA_MAX_PITCH, CAMERA_MIN_PITCH

class CameraController:
    """摄像机控制器"""
    
    def __init__(self):
        self.key_map = {
            "cam-left": False,
            "cam-right": False,
            "cam-up": False,
            "cam-down": False
        }
    
    def set_key(self, key, value):
        """设置键位状态"""
        self.key_map[key] = value
    
    def update(self, dt):
        """更新摄像机位置(每帧调用)"""
        camera = builtins.camera
        
        if self.key_map["cam-left"]:
            self._rotate_horizontal(dt, -CAMERA_ROTATION_SPEED, camera)
            
        if self.key_map["cam-right"]:
            self._rotate_horizontal(dt, CAMERA_ROTATION_SPEED, camera)
            
        if self.key_map["cam-up"]:
            self._rotate_vertical(dt, CAMERA_ROTATION_SPEED, camera)
            
        if self.key_map["cam-down"]:
            self._rotate_vertical(dt, -CAMERA_ROTATION_SPEED, camera)
    
    def _rotate_horizontal(self, dt, speed, camera):
        """水平旋转摄像机"""
        pos = camera.getPos()
        h = camera.getH()
        p = camera.getP()
        
        # 计算当前到中心的距离（只考虑XY平面的距离）
        horizontal_radius = (pos.x**2 + pos.y**2)**0.5
        h += speed * dt
        
        # 计算新的X和Y位置，保持Z不变
        new_x = horizontal_radius * math.sin(math.radians(h))
        new_y = -horizontal_radius * math.cos(math.radians(h))
        
        camera.setPos(new_x, new_y, pos.z)
        camera.setH(h)

    def _rotate_vertical(self, dt, speed, camera):
        """垂直旋转摄像机"""
        pos = camera.getPos()
        p = camera.getP()
        
        # 计算新的俯仰角
        new_p = p + speed * dt
        # new_p = max(CAMERA_MIN_PITCH, min(CAMERA_MAX_PITCH, new_p))
        
        # 如果角度没有实际变化，直接返回
        if abs(new_p - p) < 0.001:
            return
        
        # 计算水平距离
        horizontal_radius = (pos.x**2 + pos.y**2)**0.5
        
        # 计算Z轴的变化量（增量式）
        old_z_ratio = math.tan(math.radians(-p)) if abs(p) < 89 else 0
        new_z_ratio = math.tan(math.radians(-new_p)) if abs(new_p) < 89 else 0
        
        delta_z = horizontal_radius * (new_z_ratio - old_z_ratio)
        new_z = pos.z + delta_z
        
        camera.setPos(pos.x, pos.y, new_z)
        camera.setP(new_p)