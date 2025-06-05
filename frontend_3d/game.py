"""
主游戏逻辑
Panda3D 的事件系统需要传递方法引用，而不是直接调用
涉及到软件设计中的封装和接口设计原则，主类中的函数均采用包装函数
以便于在事件系统中使用，保持代码清晰和可维护
"""

import sys
import copy
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight, DirectionalLight, LVector3, BitMask32,
    LineSegs, RenderState
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
    SQUARE_SCALE, TOTAL_SQUARES
)
from utils.helpers import square_pos, square_color
from pieces.chess_pieces import Pawn
from .camera_controller import CameraController
from .mouse_picker import MousePicker

from Gomoku_ai_classical.ai import AIPlayer

class Gomoku_Start(ShowBase):
    """五子棋游戏主类"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # 五子棋游戏状态
        self.current_player = 'white'
        self.white_pieces_count = MAX_PIECES_PER_PLAYER
        self.black_pieces_count = MAX_PIECES_PER_PLAYER

        self.is_ai_enabled = True
        self.ai_side = 'black'
        self.board_size = BOARD_SIZE  # 棋盘大小
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]

        # 关键：初始化AI对象
        self.ai_player = AIPlayer()
        self.ai_thinking_text = None # AI思考状态显示

        # 初始化游戏组件
        self._setup_ui()
        self._setup_input()
        self._setup_camera()
        self._setup_lighting()
        self._setup_board()
        self._setup_controllers()
        self._start_tasks()
    
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
            text="A/D: rotate camera left/right",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.22), scale=.05)
        
        self.camera_event2 = OnscreenText(
            text="W/S: rotate camera up/down",
            parent=self.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.28), scale=.05)
        
        # 创建AI思考状态文本（初始隐藏）
        self._create_ai_thinking_text()
    
    def _setup_input(self):
        """设置输入处理"""
        self.accept('escape', sys.exit)
        
        # 摄像机控制键位
        self.accept("a", self._set_camera_key, ["cam-left", True])
        self.accept("a-up", self._set_camera_key, ["cam-left", False])
        self.accept("d", self._set_camera_key, ["cam-right", True])
        self.accept("d-up", self._set_camera_key, ["cam-right", False])
        self.accept("w", self._set_camera_key, ["cam-up", True])
        self.accept("w-up", self._set_camera_key, ["cam-up", False])
        self.accept("s", self._set_camera_key, ["cam-down", True])
        self.accept("s-up", self._set_camera_key, ["cam-down", False])
        
        # 鼠标控制
        self.accept("mouse1", self._grab_piece)
        self.accept("mouse1-up", self._release_piece)
    
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
        self.pieces = [None for _ in range(TOTAL_SQUARES)]
        
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

    def _update_gomoku_state(self, last_pos):
        """更新五子棋游戏状态"""
        # 检查胜利条件
        current_color = WHITE_3D if self.current_player == 'white' else PIECEBLACK
        row, col = last_pos // BOARD_SIZE, last_pos % BOARD_SIZE
        board_chr = 'O' if self.current_player == 'white' else 'X'
        self.board[row][col] = board_chr

        from utils.helpers import check_five_in_row
        if check_five_in_row(self.pieces, last_pos, WHITE_3D if self.current_player == 'white' else PIECEBLACK):
            winner = "White" if self.current_player == 'white' else "Black"
            print(f"🎉 Game Over! {winner} wins! Exiting in 3 seconds.")
            # 隐藏AI思考提示（如果正在显示）
            self._hide_ai_thinking()
            # 屏幕上祝賀玩家
            OnscreenText(text=f"{winner} wins! Exiting in 3 seconds.", pos=(0, 0), scale=0.1, fg=(1,0,0,1))
            # 3秒后退出
            self.taskMgr.doMethodLater(3, lambda task: self.userExit() or task.done, 'exit-task')
            return

        # 切换玩家
        if self.current_player == 'white':
            self.white_pieces_count -= 1
            self.current_player = 'black'
            print(f"轮到黑方下棋 (剩余棋子: {self.black_pieces_count})")
        else:
            self.black_pieces_count -= 1
            self.current_player = 'white'
            print(f"轮到白方下棋 (剩余棋子: {self.white_pieces_count})")

        # AI回合判断
        if self.is_ai_enabled and self.current_player == self.ai_side:
            # 显示AI思考状态，延迟执行AI移动
            self._show_ai_thinking()
            # 延迟1秒执行AI移动，让玩家看到思考提示
            self.taskMgr.doMethodLater(0.1, self._delayed_ai_move, 'ai-move-task')

    def _check_gomoku_win(self, last_pos):
        """检查五子棋胜利条件"""
        current_color = WHITE_3D if self.current_player == 'white' else PIECEBLACK
        from utils.helpers import check_five_in_row
        return check_five_in_row(self.pieces, last_pos, current_color)
    
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
        ai_chr = 'X' if self.ai_side == 'black' else 'O'
        row, col = self.ai_player.get_move(copy.deepcopy(self.board), self.board_size)
        self._hide_ai_thinking() # 隐藏思考提示
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == ' ':
            sq = row * self.board_size + col   # 这里改为 self.board_size
            self.mouse_picker.place_ai_piece(sq, ai_chr)
        else:
            print("AI无法落子")
            self._hide_ai_thinking()