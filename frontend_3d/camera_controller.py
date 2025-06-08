"""摄像机控制模块"""

import math
import time
import builtins
from utils.constants import (
    CAMERA_ROTATION_SPEED, CAMERA_MAX_PITCH, CAMERA_MIN_PITCH,
    CAMERA_ACCELERATION, CAMERA_MAX_SPEED_MULTIPLIER, CAMERA_ACCELERATION_DELAY
)
class CameraController:
    """摄像机控制器"""
    
    def __init__(self):
        self.key_map = {
            "cam-left": False,
            "cam-right": False,
            "cam-up": False,
            "cam-down": False
        }
        # 加速度相关变量
        self.key_press_start_time = {}  # 记录每个键开始按下的时间
        self.base_speed = CAMERA_ROTATION_SPEED  # 基础旋转速度
        self.acceleration = CAMERA_ACCELERATION  # 加速度系数（度/秒²）
        self.max_speed = CAMERA_ROTATION_SPEED * CAMERA_MAX_SPEED_MULTIPLIER  # 最大速度限制
        self.acceleration_delay = CAMERA_ACCELERATION_DELAY  # 开始加速前的延迟时间（秒）

    def set_key(self, key, value):
        """设置键位状态"""
        current_time = time.time()
        
        if value and not self.key_map[key]:
            # 键刚被按下
            self.key_press_start_time[key] = current_time
        elif not value and self.key_map[key]:
            # 键刚被释放
            if key in self.key_press_start_time:
                del self.key_press_start_time[key]
        
        self.key_map[key] = value

    def _get_current_speed(self, key):
        """根据按键持续时间计算当前旋转速度"""
        if key not in self.key_press_start_time:
            return self.base_speed
        
        # 计算持续时间
        hold_time = time.time() - self.key_press_start_time[key]
        
        # 延迟开始加速
        if hold_time < self.acceleration_delay:
            return self.base_speed
        
        # 计算加速时间（减去延迟时间）
        accel_time = hold_time - self.acceleration_delay
        
        # 计算当前速度：基础速度 + 加速度 × 时间
        current_speed = self.base_speed + (self.acceleration * accel_time)
        
        # 限制最大速度
        return min(current_speed, self.max_speed)
    
    def update(self, dt):
        """更新摄像机位置(每帧调用)"""
        camera = builtins.camera
        
        if self.key_map["cam-left"]:
            speed = self._get_current_speed("cam-left")
            self._rotate_horizontal(dt, -speed, camera)
            
        if self.key_map["cam-right"]:
            speed = self._get_current_speed("cam-right")
            self._rotate_horizontal(dt, speed, camera)
            
        if self.key_map["cam-up"]:
            speed = self._get_current_speed("cam-up")
            self._rotate_vertical(dt, -speed, camera)
            
        if self.key_map["cam-down"]:
            speed = self._get_current_speed("cam-down")
            self._rotate_vertical(dt, speed, camera)
    
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