from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Vec3, BitMask32
from panda3d.core import CollisionTraverser, CollisionNode, CollisionSphere, CollisionHandlerPusher,CollisionBox,Point3
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from frontend_3d.setup_scene import SceneSetup
from frontend_3d.setup_board import BoardSetup
import sys

class CSGOCameraDemo:
    def __init__(self, base):
        self.base = base

        # 自动转发 base 的所有属性
        for attr in dir(base):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(base, attr))

        self.disableMouse()
        self.setup_camera()

        # 初始化场景和棋盘外观
        self.scene_setup = SceneSetup(self.loader, self.render, self.taskMgr)
        self.scene_setup.setup_lighting()
        self.scene_setup.load_scene()
        self.ground = self.scene_setup.ground_model

        self.board_setup = BoardSetup(self.loader, self.render)
        self.board_setup.setup_board()

        # 鼠标灵敏度
        self.mouse_sensitivity = 0.2

        # 键盘移动速度
        self.move_speed = 5

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

        # ----------- 碰撞检测部分 -----------
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # 给摄像机加碰撞球
        camera_sphere = CollisionSphere(0, 0, 0, 5)
        camera_cnode = CollisionNode('camera')
        camera_cnode.addSolid(camera_sphere)
        camera_cnode.setFromCollideMask(BitMask32.bit(1))
        camera_cnode.setIntoCollideMask(BitMask32.allOff())
        self.camera_collider = self.camera.attachNewNode(camera_cnode)

        # 注册到碰撞系统
        self.pusher.addCollider(self.camera_collider, self.camera)
        self.cTrav.addCollider(self.camera_collider, self.pusher)

        self.wall_nodes = []

        # 左墙（x=60）
        left_wall = self.ground.attachNewNode(CollisionNode('left_wall'))
        left_wall.node().addSolid(CollisionBox(Point3(5, 0, 5), 1, 1000, 50))  # x=60，y方向很长，z中心=5
        left_wall.node().setIntoCollideMask(BitMask32.bit(1))
        self.wall_nodes.append(left_wall)

        # 右墙（x=-60）
        right_wall = self.ground.attachNewNode(CollisionNode('right_wall'))
        right_wall.node().addSolid(CollisionBox(Point3(-5, 0, 5), 1, 1000, 50))
        right_wall.node().setIntoCollideMask(BitMask32.bit(1))
        self.wall_nodes.append(right_wall)

        # 后墙（y=85.27）
        back_wall = self.ground.attachNewNode(CollisionNode('back_wall'))
        back_wall.node().addSolid(CollisionBox(Point3(0, 4, 5), 100, 1, 100))
        back_wall.node().setIntoCollideMask(BitMask32.bit(1))
        self.wall_nodes.append(back_wall)

        # 前墙（y=-900）
        front_wall = self.ground.attachNewNode(CollisionNode('front_wall'))
        front_wall.node().addSolid(CollisionBox(Point3(0, -45, 5), 100, 1, 100))
        front_wall.node().setIntoCollideMask(BitMask32.bit(1))
        self.wall_nodes.append(front_wall)
        # -----------------------------------

        # 添加摄像机位置显示文本
        self.cam_pos_text = OnscreenText(
            text="",
            pos=(-1.3, 0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=0,
            parent=self.aspect2d
        )

        # 任务
        self.taskMgr.add(self.update_camera, "UpdateCameraTask")
        self.last_mouse_pos = None

        # Gomoku 相关
        self.in_gomoku_area = False
        self.hint_text = None
        self.taskMgr.add(self.check_gomoku_area, "CheckGomokuArea")

    def setup_camera(self):
        self.base.camera.setPos(0, -35, 5)
        self.pitch = 0
        self.yaw = 0

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
        self.cam_pos_text.setText(f"Camera Pos: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
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

    def cleanup(self):
        # 清理场景、任务、UI等
        if self.hint_text:
            self.hint_text.destroy()
        self.base.taskMgr.remove("CheckGomokuArea")
        self.base.taskMgr.remove("UpdateCameraTask")
        self.cam_pos_text.destroy()
        # 清理模型
        if hasattr(self, "scene_setup"):
            self.scene_setup.cleanup()
        if hasattr(self, "board_setup"):
            self.board_setup.cleanup()
        # 清理墙体碰撞模型
        if hasattr(self, "wall_nodes"):
            for node in self.wall_nodes:
                node.removeNode()
            self.wall_nodes.clear()

    def restore_camera(self, pos, hpr):
        self.base.camera.setPos(pos)
        self.base.camera.setHpr(hpr)