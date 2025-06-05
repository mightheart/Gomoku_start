"""
主游戏逻辑
Panda3D 的事件系统需要传递方法引用，而不是直接调用
涉及到软件设计中的封装和接口设计原则，主类中的函数均采用包装函数
以便于在事件系统中使用，保持代码清晰和可维护
"""

import sys
import copy
import time
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight, DirectionalLight, LVector3, BitMask32,
    LineSegs, RenderState, Texture, CardMaker
)
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from direct.showbase import DirectObject
import builtins  # 移到顶部统一管理

from utils.constants import (
    CAMERA_INITIAL_POSITION, CAMERA_INITIAL_ANGLES,
    WHITE_3D, PIECEBLACK, 
    MAX_PIECES_PER_PLAYER,BOARD_SIZE,PIECE_DRAG_HEIGHT,TOTAL_SQUARES,
    WHITE_BOX_POS, BLACK_BOX_POS, BOX_SIZE,
    SQUARE_SCALE, TOTAL_SQUARES,
    PLAYER_WHITE, PLAYER_BLACK,
    PIECE_BLACK, PIECE_WHITE,
    BACKGROUND_POSITION  # 导入背景位置常量
)
from utils.helpers import square_pos, square_color
from utils.chessboard import ChessBoard
from pieces.chess_pieces import Pawn
from .camera_controller import CameraController
from .mouse_picker import MousePicker

from Gomoku_ai_classical.ai import AIPlayer

class Gomoku_Start(ShowBase):
    """五子棋游戏主类"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # 五子棋游戏状态
        self.current_player = PLAYER_WHITE
        self.white_pieces_count = MAX_PIECES_PER_PLAYER
        self.black_pieces_count = MAX_PIECES_PER_PLAYER

        self.is_ai_enabled = True
        self.ai_side = PLAYER_BLACK
        self.chessboard = ChessBoard(size=BOARD_SIZE)  # 初始化棋盘对象

        # 关键：初始化AI对象
        self.ai_player = AIPlayer()
        self.ai_thinking_text = None # AI思考状态显示

        # 三连击检测变量
        self.key_press_times = {}  # 存储每个键的按下时间
        self.key_press_counts = {}  # 存储每个键的连续按下次数
        self.triple_click_threshold = 0.5  # 三连击时间阈值（秒）
        self.auto_rotate_active = {}  # 存储自动旋转状态
        self.auto_rotate_task = None  # 自动旋转任务

        # 初始化游戏组件
        self._setup_ui()
        self._setup_input()
        self._setup_camera()
        self._setup_lighting()
        self._setup_board()
        self._setup_controllers()
        self._start_tasks()
        
        # 加载并渲染背景图片
        self._load_and_render_background()
    
    def _setup_ui(self):
        """设置用户界面"""
        self.title = OnscreenText(
            text="Gomoku Game",  # 标题
            style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
            pos=(0.8, -0.95), scale=.07)
        
        self.escape_event = OnscreenText(
            text="ESC: Exit Gomoku", parent=self.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale=.05)
        
        self.mouse1_event = OnscreenText(
            text="Left Click & Drag: Grab & Release Piece",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.16), scale=.05)
        
        self.camera_event1 = OnscreenText(
            text="A/D: rotate camera left/right (Triple click for auto)",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.22), scale=.05)
        
        self.camera_event2 = OnscreenText(
            text="W/S: rotate camera up/down (Triple click for auto)",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.28), scale=.05)
        
        self.space_event = OnscreenText(
            text="SPACE: Stop auto rotation",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.34), scale=.05)
        
        # 创建AI思考状态文本（初始隐藏）
        self._create_ai_thinking_text()
    
    def _setup_input(self):
        """设置输入处理"""
        self.accept('escape', sys.exit)
        
        # 摄像机控制键位（修改为支持三连击检测）
        self.accept("a", self._handle_key_press, ["cam-left"])
        self.accept("a-up", self._set_camera_key, ["cam-left", False])
        self.accept("d", self._handle_key_press, ["cam-right"])
        self.accept("d-up", self._set_camera_key, ["cam-right", False])
        self.accept("w", self._handle_key_press, ["cam-up"])
        self.accept("w-up", self._set_camera_key, ["cam-up", False])
        self.accept("s", self._handle_key_press, ["cam-down"])
        self.accept("s-up", self._set_camera_key, ["cam-down", False])
        
        # 添加空格键停止自动旋转
        self.accept("space", self._stop_auto_rotate)
        
        # 鼠标控制
        self.accept("mouse1", self._grab_piece)
        self.accept("mouse1-up", self._release_piece)
    
    def _handle_key_press(self, key):
        """处理键盘按下事件，检测三连击"""
        current_time = time.time()
        
        # 初始化键的记录
        if key not in self.key_press_times:
            self.key_press_times[key] = []
            self.key_press_counts[key] = 0
            self.auto_rotate_active[key] = False
        
        # 清理过期的按键记录
        self.key_press_times[key] = [t for t in self.key_press_times[key] 
                                    if current_time - t <= self.triple_click_threshold]
        
        # 记录当前按键时间
        self.key_press_times[key].append(current_time)
        
        # 检测是否达到三连击
        if len(self.key_press_times[key]) >= 3:
            # 检查最近三次按键是否在时间阈值内
            recent_times = self.key_press_times[key][-3:]
            if recent_times[-1] - recent_times[0] <= self.triple_click_threshold:
                print(f"检测到 {key} 三连击！开始自动旋转")
                self._start_auto_rotate(key)
                # 清空记录，避免重复触发
                self.key_press_times[key] = []
                return
        
        # 普通按键处理
        self._set_camera_key(key, True)

    def _start_auto_rotate(self, direction):
        """开始自动旋转"""
        # 停止之前的自动旋转
        self._stop_auto_rotate()
        
        # 设置新的自动旋转方向
        for key in self.auto_rotate_active:
            self.auto_rotate_active[key] = False
        self.auto_rotate_active[direction] = True
        
        # 启动自动旋转任务
        self.auto_rotate_task = self.taskMgr.add(self._auto_rotate_task, 'autoRotateTask')
        
        # 显示提示信息
        if hasattr(self, 'auto_rotate_hint'):
            self.auto_rotate_hint.destroy()
        
        direction_text = {
            'cam-left': '左旋转',
            'cam-right': '右旋转', 
            'cam-up': '上旋转',
            'cam-down': '下旋转'
        }
        
        self.auto_rotate_hint = OnscreenText(
            text=f"自动{direction_text.get(direction, '旋转')}中... (按空格键停止)",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 0, 1), pos=(0.06, -0.4), scale=.05)

    def _stop_auto_rotate(self):
        """停止自动旋转"""
        # 停止自动旋转任务
        if self.auto_rotate_task:
            self.taskMgr.remove(self.auto_rotate_task)
            self.auto_rotate_task = None
        
        # 重置所有自动旋转状态
        for key in self.auto_rotate_active:
            self.auto_rotate_active[key] = False
        
        # 停止所有摄像机键状态
        self.camera_controller.set_key('cam-left', False)
        self.camera_controller.set_key('cam-right', False)
        self.camera_controller.set_key('cam-up', False)
        self.camera_controller.set_key('cam-down', False)
        
        # 移除提示文本
        if hasattr(self, 'auto_rotate_hint'):
            self.auto_rotate_hint.destroy()
            delattr(self, 'auto_rotate_hint')
        
        print("自动旋转已停止")

    def _auto_rotate_task(self, task):
        """自动旋转任务"""
        # 检查哪个方向需要自动旋转
        for direction, active in self.auto_rotate_active.items():
            if active:
                self.camera_controller.set_key(direction, True)
            else:
                self.camera_controller.set_key(direction, False)
        
        return task.cont

    def _setup_camera(self):
        """设置摄像机初始位置和角度"""
        self.disableMouse()
        self.camera.setPosHpr(CAMERA_INITIAL_POSITION[0], CAMERA_INITIAL_POSITION[1], CAMERA_INITIAL_POSITION[2],
                               CAMERA_INITIAL_ANGLES[0], CAMERA_INITIAL_ANGLES[1], CAMERA_INITIAL_ANGLES[2])
    
    def _setup_lighting(self):
        """设置光照"""
        ambient_light = AmbientLight("ambientLight")
        ambient_light.setColor((.8, .8, .8, 1))
        
        directional_light = DirectionalLight("directionalLight")
        directional_light.setDirection(LVector3(0, 45, -45))
        directional_light.setColor((0.2, 0.2, 0.2, 1))
        
        self.render.setLight(self.render.attachNewNode(directional_light))
        self.render.setLight(self.render.attachNewNode(ambient_light))
    
    def _setup_board(self):
        """设置15x15五子棋棋盘"""
        self.square_root = self.render.attachNewNode("squareRoot")
        
        # 15x15棋盘，225个格子
        self.squares = [None for _ in range(TOTAL_SQUARES)]
        self.pieces = [None for _ in range(TOTAL_SQUARES)]  # 保留用于渲染
        
        # 创建棋盘格子
        for i in range(TOTAL_SQUARES):
            self.squares[i] = self.loader.loadModel("models/square")
            self.squares[i].reparentTo(self.square_root)
            self.squares[i].setPos(square_pos(i))
            self.squares[i].setColor(square_color(i))
            self.squares[i].setScale(SQUARE_SCALE)  # 缩放格子
            
            # 设置碰撞检测
            self.squares[i].find("**/polygon").node().setIntoCollideMask(BitMask32.bit(1))
            self.squares[i].find("**/polygon").node().setTag('square', str(i))
        
        # 绘制15x15五子棋网格线
        self._draw_gomoku_grid()
        
        # 创建棋盒
        self._setup_piece_boxes()

    def _setup_piece_boxes(self):
        """设置棋盒"""
        print("开始创建棋盒...")
    
        # 创建白棋盒
        self.white_box = self.loader.loadModel("models/square")
        if self.white_box:
            self.white_box.reparentTo(self.render)
            self.white_box.setPos(WHITE_BOX_POS)
            self.white_box.setColor(WHITE_3D)
            self.white_box.setScale(BOX_SIZE, BOX_SIZE, 0.2)
            
            # 设置碰撞检测
            polygon_node = self.white_box.find("**/polygon")
            if polygon_node:
                polygon_node.node().setIntoCollideMask(BitMask32.bit(1))
                polygon_node.node().setTag('piece_box', 'white')
                print(f"白棋盒创建成功，位置: {WHITE_BOX_POS}")
            else:
                print("警告: 白棋盒没有找到碰撞多边形")
        else:
            print("错误: 无法加载白棋盒模型")
        
        # 创建黑棋盒
        self.black_box = self.loader.loadModel("models/square")
        if self.black_box:
            self.black_box.reparentTo(self.render)
            self.black_box.setPos(BLACK_BOX_POS)
            self.black_box.setColor(PIECEBLACK)
            self.black_box.setScale(BOX_SIZE, BOX_SIZE, 0.2)
            
            # 设置碰撞检测
            polygon_node = self.black_box.find("**/polygon")
            if polygon_node:
                polygon_node.node().setIntoCollideMask(BitMask32.bit(1))
                polygon_node.node().setTag('piece_box', 'black')
                print(f"黑棋盒创建成功，位置: {BLACK_BOX_POS}")
            else:
                print("警告: 黑棋盒没有找到碰撞多边形")
        else:
            print("错误: 无法加载黑棋盒模型")

    def switch_player(self):
        """切换玩家"""
        # 切换玩家
        if self.current_player == PLAYER_WHITE:
            self.white_pieces_count -= 1
            self.current_player = PLAYER_BLACK
            print(f"轮到黑方下棋 (剩余棋子: {self.black_pieces_count})")
        else:
            self.black_pieces_count -= 1
            self.current_player = PLAYER_WHITE
            print(f"轮到白方下棋 (剩余棋子: {self.white_pieces_count})")
        
    def check_winner(self):
        """检查是否有玩家获胜"""
        if self.chessboard.check_board_winner():
            if self.chessboard.winner != 0:
                print(f"玩家{self.chessboard.winner}获胜！")
                return True
            return False
    
    def _update_gomoku_state(self, last_pos):
        """更新五子棋游戏状态"""
        # 切换玩家
        self.switch_player()
        
        # 重新渲染所有棋子
        self._render_all_pieces()
        
        # 检查胜利条件
        if self.check_winner():
            winner = "White" if self.chessboard.winner == PLAYER_WHITE else "Black"
            print(f"🎉 Game Over! {winner} wins! Exiting in 3 seconds.")
            # 隐藏AI思考提示（如果正在显示）
            self._hide_ai_thinking()
            # 屏幕上祝賀玩家
            OnscreenText(text=f"{winner} wins! Exiting in 3 seconds.", pos=(0, 0), scale=0.1, fg=(1,0,0,1))
            # 3秒后退出
            self.taskMgr.doMethodLater(30, lambda task: self.userExit() or task.done, 'exit-task')
            time.sleep(5)
            return
        
        # AI回合判断
        if self.is_ai_enabled and self.current_player == self.ai_side:
            # 显示AI思考状态，延迟执行AI移动
            self._show_ai_thinking()
            # 延迟1秒执行AI移动，让玩家看到思考提示
            self.taskMgr.doMethodLater(0.1, self._delayed_ai_move, 'ai-move-task')
    
    def _draw_gomoku_grid(self):
        """绘制15x15五子棋网格线"""
        lines = LineSegs()
        lines.setThickness(1.5)  # 稍微细一点
        lines.setColor(0, 0, 0, 1)
        
        # 计算网格范围：从-7到+7，共15条线
        grid_range = 7 * SQUARE_SCALE  # 网格的边界
        
        # 绘制横线 (15条)
        for row in range(BOARD_SIZE):
            y_pos = grid_range - row * SQUARE_SCALE
            lines.moveTo(-grid_range, y_pos, 0.01)
            lines.drawTo(grid_range, y_pos, 0.01)
        
        # 绘制竖线 (15条)
        for col in range(BOARD_SIZE):
            x_pos = -grid_range + col * SQUARE_SCALE
            lines.moveTo(x_pos, grid_range, 0.01)
            lines.drawTo(x_pos, -grid_range, 0.01)
        
        # 创建线条节点并添加到场景
        grid_node = self.render.attachNewNode(lines.create())
        grid_node.reparentTo(self.square_root)
    
    def _setup_controllers(self):
        """设置控制器"""
        self.camera_controller = CameraController()
        self.mouse_picker = MousePicker(self)
        self.mouse_picker.set_board_data(self.squares, self.pieces)
        # 添加游戏实例引用，让鼠标拾取器能访问游戏状态
        self.mouse_picker.set_game_instance(self)
    
    def _start_tasks(self):
        """启动任务"""
        self.mouse_task = self.taskMgr.add(self._mouse_task, 'mouseTask')
        self.move_task = self.taskMgr.add(self._move_task, 'move')
    
    def _set_camera_key(self, key, value):
        """设置摄像机控制键状态"""
        self.camera_controller.set_key(key, value)
    
    def _grab_piece(self):
        """抓取棋子"""
        self.mouse_picker.grab_piece()
    
    def _release_piece(self):
        """释放棋子"""
        self.mouse_picker.release_piece()
    
    def _mouse_task(self, task):
        """鼠标任务"""
        return self.mouse_picker.update(self.mouseWatcherNode, self.square_root)
    
    def _move_task(self, task):
        """摄像机移动任务"""
        # 使用全局时钟获取帧间隔时间
        dt = builtins.globalClock.getDt()
        self.camera_controller.update(dt)
        return task.cont

    def _create_ai_thinking_text(self):
        """创建AI思考状态显示文本"""
        self.ai_thinking_text = OnscreenText(
            text="AI thinking......",
            parent=self.a2dTopRight,
            align=TextNode.ARight,
            style=1, 
            fg=(1, 1, 0, 1),  # 黄色文字
            shadow=(0, 0, 0, 1),  # 黑色阴影
            pos=(-0.06, -0.1),  # 右上角位置
            scale=0.06
        )
        self.ai_thinking_text.hide()  # 初始隐藏

    def _show_ai_thinking(self):
        """显示AI思考状态"""
        if self.ai_thinking_text:
            self.ai_thinking_text.show()

    def _hide_ai_thinking(self):
        """隐藏AI思考状态"""
        if self.ai_thinking_text:
            self.ai_thinking_text.hide()

    def _delayed_ai_move(self, task):
        """延迟执行AI移动"""
        self.do_ai_move()
        return task.done
    
    
    def do_ai_move(self):
        """AI自动落子"""
        old_chessboard = copy.deepcopy(self.chessboard)
        self.chessboard = self.ai_player.get_next_chessboard(self.chessboard, self.ai_side)
        self._hide_ai_thinking() # 隐藏思考提示
        
        # 重新渲染所有棋子
        self._render_all_pieces()
        
        # 切换玩家
        self.switch_player()
        
        # 检查胜利条件
        if self.check_winner():
            winner = "White" if self.chessboard.winner == PLAYER_WHITE else "Black"
            print(f"🎉 Game Over! {winner} wins! Exiting in 3 seconds.")
            OnscreenText(text=f"{winner} wins! Exiting in 3 seconds.", pos=(0, 0), scale=0.1, fg=(1,0,0,1))
            self.taskMgr.doMethodLater(3, lambda task: self.userExit() or task.done, 'exit-task')

    def _render_all_pieces(self):
        """根据chessboard重新渲染所有棋子"""
        # 销毁所有现有棋子
        for i in range(TOTAL_SQUARES):
            if self.pieces[i] is not None:
                self.pieces[i].obj.removeNode()
                self.pieces[i] = None
        
        # 根据chessboard重新创建棋子
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece_type = self.chessboard.get_stone(row, col)
                if piece_type != ' ':  # 不是空位
                    square_index = row * BOARD_SIZE + col
                    
                    # 根据棋子类型确定颜色
                    if piece_type == PIECE_BLACK:
                        color = PIECEBLACK
                    elif piece_type == PIECE_WHITE:
                        color = WHITE_3D
                    else:
                        continue
                    
                    # 创建棋子
                    piece = Pawn(square_index, color, self)
                    piece.obj.setPos(square_pos(square_index))
                    self.pieces[square_index] = piece
        
        print("所有棋子重新渲染完成")

    def _load_and_render_background(self):
        """加载并渲染背景图片"""
        try:
            background_texture = self.loader.loadTexture("models/background2.jpg")
            card_maker = CardMaker("background")
            card_maker.setFrame(-1, 1, -1, 1)  # 设置平面大小
            background_card = self.render.attachNewNode(card_maker.generate())
            background_card.setTexture(background_texture)
            background_card.setPos(*BACKGROUND_POSITION)  # 使用常量设置位置
            background_card.setScale(20)  # 根据需要调整大小
            print("背景图片加载成功")
        except Exception as e:
            print(f"背景图片加载失败: {e}")

