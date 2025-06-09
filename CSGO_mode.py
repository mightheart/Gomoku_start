from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Vec3, Filename,AmbientLight,DirectionalLight,LVector3
from direct.task import Task
import sys

class CSGOCameraDemo(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self._setup_lighting()
        # 加载地面模型
        self.ground = self.loader.loadModel("models/kk.bam")
        self.ground.reparentTo(self.render)
        self.ground.setPos(0, 0, -10)
        self.ground.setScale(100)
        self.ground.setHpr(180, 0, 0)

        # 摄像机初始位置和角度
        self.camera.setPos(0, -30, 5)
        self.pitch = 0
        self.yaw = 0

        # 鼠标灵敏度
        self.mouse_sensitivity = 0.2

        # 键盘移动速度
        self.move_speed = 10

        # 隐藏鼠标光标并锁定到窗口中心
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)

        # 按键状态
        self.key_map = {"w": False, "s": False, "a": False, "d": False}

        # 绑定按键
        for key in self.key_map:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("escape", sys.exit)

        # 任务
        self.taskMgr.add(self.update_camera, "UpdateCameraTask")

        # 上一帧鼠标位置
        self.last_mouse_pos = None


    def set_key(self, key, value):
        self.key_map[key] = value

    def update_camera(self, task):
        # 鼠标视角
        if self.mouseWatcherNode.hasMouse():
            x = self.win.getPointer(0).getX()
            y = self.win.getPointer(0).getY()
            win_cx = self.win.getXSize() // 2
            win_cy = self.win.getYSize() // 2
            if self.last_mouse_pos is not None:
                dx = x - win_cx
                dy = y - win_cy
                self.yaw -= dx * self.mouse_sensitivity
                self.pitch -= dy * self.mouse_sensitivity
                self.pitch = max(-89, min(89, self.pitch))
                self.camera.setHpr(self.yaw, self.pitch, 0)
            # 鼠标重置到中心
            self.win.movePointer(0, win_cx, win_cy)
            self.last_mouse_pos = (win_cx, win_cy)

        # 键盘移动
        dir_vec = Vec3(0, 0, 0)
        quat = self.camera.getQuat()
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
            self.camera.setPos(self.camera.getPos() + dir_vec * self.move_speed)
        return Task.cont
    def _setup_lighting(self):
            """设置光照"""
            ambient_light = AmbientLight("ambientLight")
            ambient_light.setColor((.8, .8, .8, 1))
            
            directional_light = DirectionalLight("directionalLight")
            directional_light.setDirection(LVector3(0, 45, -45))
            directional_light.setColor((0.2, 0.2, 0.2, 1))
            
            self.render.setLight(self.render.attachNewNode(directional_light))
            self.render.setLight(self.render.attachNewNode(ambient_light))
            

if __name__ == "__main__":
    app = CSGOCameraDemo()
    app.run()