"""
主游戏逻辑 - 重构版本
"""
import time
import copy
import builtins
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import (
    AmbientLight, DirectionalLight, LVector3, BitMask32,
    LineSegs, CardMaker, Material, GeomNode, GeomVertexFormat,
    GeomVertexData, Geom, GeomVertexWriter, GeomPoints, RenderModeAttrib
)

from utils.constants import *
from utils.helpers import square_pos, square_color
from utils.chessboard import ChessBoard
from pieces.chess_pieces import Pawn
from .camera_controller import CameraController
from .mouse_picker import MousePicker
from .audio_manager import AudioManager
from .ui_manager import UIManager
from .game_statistics import GameStatistics
from .effects_manager import EffectsManager
from .input_manager import InputManager
from Gomoku_ai_classical.ai import AIPlayer

class Gomoku_Start(ShowBase):
    """五子棋游戏主类 - 重构版本"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # 游戏状态
        self.current_player = PLAYER_WHITE
        self.white_pieces_count = MAX_PIECES_PER_PLAYER
        self.black_pieces_count = MAX_PIECES_PER_PLAYER
        self.is_ai_enabled = True
        self.ai_side = PLAYER_BLACK
        self.game_over = False
        
        # 游戏组件
        self.chessboard = ChessBoard(size=BOARD_SIZE)
        self.ai_player = AIPlayer()
        
        # 棋盘数据
        self.squares = [None for _ in range(TOTAL_SQUARES)]
        self.pieces = [None for _ in range(TOTAL_SQUARES)]
        
        # 初始化管理器
        self._init_managers()
        
        # 初始化游戏组件
        self._setup_camera()
        self._setup_lighting()
        self._setup_board()
        self._start_tasks()
        
        # 加载场景
        self._load_scene()
    
    def _init_managers(self):
        """初始化所有管理器"""
        self.audio_manager = AudioManager(self.loader, self.taskMgr)
        self.ui_manager = UIManager(self)
        self.statistics = GameStatistics()
        self.effects_manager = EffectsManager(self.render, self.taskMgr)
        
        # 创建控制器
        self.camera_controller = CameraController()
        self.mouse_picker = MousePicker(self)
        
        # 输入管理器需要在控制器创建后初始化
        self.input_manager = InputManager(self, self.camera_controller)
        
        # 设置引用
        self.mouse_picker.set_board_data(self.squares, self.pieces)
        self.mouse_picker.set_game_instance(self)
    
    def _setup_camera(self):
        """设置摄像机"""
        self.disableMouse()
        self.camera.setPos(*CAMERA_INITIAL_POSITION)
        self.camera.setHpr(*CAMERA_INITIAL_ANGLES)
        self.camera.setX(self.camera.getX() + 0)
        self.camera.setY(self.camera.getY() + -4)
        self.camera.setZ(self.camera.getZ() + 0)
        self.camera.setP(self.camera.getP() + 10)
    
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
        """设置棋盘"""
        self.square_root = self.render.attachNewNode("squareRoot")
        
        # 创建棋盘格子
        for i in range(TOTAL_SQUARES):
            self.squares[i] = self.loader.loadModel("models/square")
            self.squares[i].reparentTo(self.square_root)
            self.squares[i].setPos(square_pos(i))
            self.squares[i].setColor(square_color(i))
            self.squares[i].setScale(SQUARE_SCALE)
            
            # 设置碰撞检测
            self.squares[i].find("**/polygon").node().setIntoCollideMask(BitMask32.bit(1))
            self.squares[i].find("**/polygon").node().setTag('square', str(i))
        
        # 为棋盘格子添加厚度
        for square in self.squares:
            square.setScale(square.getScale()[0], square.getScale()[1], 0.1)
        
        # 绘制网格线
        self._draw_gomoku_grid()
        
        # 创建棋盒
        self._setup_piece_boxes()
        
        # 加载棋盘装饰
        self._load_board_decorations()
    
    def _draw_gomoku_grid(self):
        """绘制网格线"""
        lines = LineSegs()
        lines.setThickness(1.5)
        lines.setColor(0, 0, 0, 1)
        
        grid_range = 7 * SQUARE_SCALE
        
        # 横线
        for row in range(BOARD_SIZE):
            y_pos = grid_range - row * SQUARE_SCALE
            lines.moveTo(-grid_range, y_pos, 0.01)
            lines.drawTo(grid_range, y_pos, 0.01)
        
        # 竖线
        for col in range(BOARD_SIZE):
            x_pos = -grid_range + col * SQUARE_SCALE
            lines.moveTo(x_pos, grid_range, 0.01)
            lines.drawTo(x_pos, -grid_range, 0.01)
        
        grid_node = self.render.attachNewNode(lines.create())
        grid_node.reparentTo(self.square_root)
    
    def _setup_piece_boxes(self):
        """设置棋盒"""
        # 白棋盒
        self.white_box = self.loader.loadModel("models/square")
        if self.white_box:
            self.white_box.reparentTo(self.render)
            self.white_box.setPos(WHITE_BOX_POS)
            self.white_box.setTransparency(True)
            self.white_box.setColor(1, 1, 1, 0)
            self.white_box.setScale(BOX_SIZE, BOX_SIZE, 0.2)
            
            polygon_node = self.white_box.find("**/polygon")
            if polygon_node:
                polygon_node.node().setIntoCollideMask(BitMask32.bit(1))
                polygon_node.node().setTag('piece_box', 'white')
        
        # 黑棋盒
        self.black_box = self.loader.loadModel("models/square")
        if self.black_box:
            self.black_box.reparentTo(self.render)
            self.black_box.setPos(BLACK_BOX_POS)
            self.black_box.setTransparency(True)
            self.black_box.setColor(1, 1, 1, 0)
            self.black_box.setScale(BOX_SIZE, BOX_SIZE, 0.2)
            
            polygon_node = self.black_box.find("**/polygon")
            if polygon_node:
                polygon_node.node().setIntoCollideMask(BitMask32.bit(1))
                polygon_node.node().setTag('piece_box', 'black')
        
        # 加载棋盒装饰
        self._load_piece_box_decorations()
    
    def _load_board_decorations(self):
        """加载棋盘装饰"""
        # 棋盘厚度模型
        thickness_model = self.loader.loadModel("models/qi_pan.obj")
        if thickness_model:
            thickness_model.reparentTo(self.square_root)
            thickness_model.setPos(*THICKNESS_POSITION_OFFSET)
            thickness_model.setScale(
                BOARD_SIZE * SQUARE_SCALE * THICKNESS_SCALE[0],
                BOARD_SIZE * SQUARE_SCALE * THICKNESS_SCALE[1],
                THICKNESS_SCALE[2]
            )
            thickness_model.setColor(0.71, 0.55, 0.35, 1)
        
        # 对手模型
        opponent_model = self.loader.loadModel("models/Raiden shogun.glb")
        if opponent_model:
            opponent_model.reparentTo(self.square_root)
            opponent_model.setPos(*OPPONENT_MODEL_POSITION)
            opponent_model.setScale(*OPPONENT_MODEL_SCALE)
            opponent_model.setHpr(*OPPONENT_MODEL_ROTATION)
    
    def _load_piece_box_decorations(self):
        """加载棋盒装饰"""
        # 白棋盒装饰
        decoration_white = self.loader.loadModel("models/qihe.obj")
        if decoration_white:
            decoration_white.reparentTo(self.render)
            decoration_white.setPos(
                WHITE_BOX_POS[0] + DECORATION_POSITION_OFFSET[0],
                WHITE_BOX_POS[1] + DECORATION_POSITION_OFFSET[1],
                WHITE_BOX_POS[2] + DECORATION_POSITION_OFFSET[2]
            )
            decoration_white.setScale(DECORATION_SCALE_X, DECORATION_SCALE_Y, DECORATION_SCALE_Z)
            decoration_white.setHpr(*DECORATION_ROTATION)
            decoration_white.setColor(WHITE_3D)
        
        # 黑棋盒装饰
        decoration_black = self.loader.loadModel("models/qihe.obj")
        if decoration_black:
            decoration_black.reparentTo(self.render)
            decoration_black.setPos(
                BLACK_BOX_POS[0] + DECORATION_POSITION_OFFSET[0],
                BLACK_BOX_POS[1] + DECORATION_POSITION_OFFSET[1],
                BLACK_BOX_POS[2] + DECORATION_POSITION_OFFSET[2]
            )
            decoration_black.setScale(DECORATION_SCALE_X, DECORATION_SCALE_Y, DECORATION_SCALE_Z)
            decoration_black.setHpr(*DECORATION_ROTATION)
            decoration_black.setColor(PIECEBLACK)
    
    def _start_tasks(self):
        """启动任务"""
        self.mouse_task = self.taskMgr.add(self._mouse_task, 'mouseTask')
        self.move_task = self.taskMgr.add(self._move_task, 'move')
    
    def _mouse_task(self, task):
        """鼠标任务"""
        return self.mouse_picker.update(self.mouseWatcherNode, self.square_root)
    
    def _move_task(self, task):
        """主循环任务"""
        dt = builtins.globalClock.getDt()
        self.camera_controller.update(dt)
        
        if not self.game_over:
            self.statistics.update_player_time(self.current_player, self.game_over)
            game_data = self.statistics.get_game_data()
            self.ui_manager.update_statistics(game_data)
            self.ui_manager.update_current_player(
                self.current_player, self.is_ai_enabled, self.ai_side, self.game_over)
        
        return task.cont
    
    def _load_scene(self):
        """加载场景模型"""
        # 背景
        try:
            background_texture = self.loader.loadTexture("models/background2.jpg")
            card_maker = CardMaker("background")
            card_maker.setFrame(-1, 1, -1, 1)
            background_card = self.render.attachNewNode(card_maker.generate())
            background_card.setTexture(background_texture)
            background_card.setPos(*BACKGROUND_POSITION)
            background_card.setScale(20)
        except Exception as e:
            print(f"背景加载失败: {e}")
        
        # 地面
        try:
            ground_model = self.loader.loadModel("models/kk.bam")
            ground_model.reparentTo(self.render)
            ground_model.setPos(0, 0, -5)
            ground_model.setScale(20)
            ground_model.setHpr(180, 0, 0)
        except Exception as e:
            print(f"地面模型加载失败: {e}")
        
        # 角色模型
        self._load_character_models()
        
        # 星空
        self._load_starfield()
    
    def _load_character_models(self):
        """加载角色模型"""
        # 雷电将军
        try:
            self.leidian_model = Actor("models/yae-miko_genshin-impact.bam")
            self.leidian_model.reparentTo(self.render)
            self.leidian_model.setPos(-15, 20, -10)
            self.leidian_model.setScale(15)
            
            self.leidian_anims = self.leidian_model.getAnimNames()
            self.current_anim_index = 0
            
            if self.leidian_anims:
                self.leidian_model.play(self.leidian_anims[self.current_anim_index])
                self.taskMgr.add(self._check_anim_completion, "checkAnimCompletion")
        except Exception as e:
            print(f"雷电将军模型加载失败: {e}")
        
        # 瑶瑶
        try:
            self.yaoyao_model = self.loader.loadModel("models/Yaoyao - Genshin Impact.bam")
            self.yaoyao_model.reparentTo(self.render)
            self.yaoyao_model.setPos(-15, -20, -10)
            self.yaoyao_model.setScale(15)
        except Exception as e:
            print(f"瑶瑶模型加载失败: {e}")
    
    def _check_anim_completion(self, task):
        """检查动画完成"""
        if not hasattr(self, 'leidian_model') or self.leidian_model.isEmpty():
            return task.done
        
        if not self.leidian_anims:
            return task.done
        
        current_anim = self.leidian_anims[self.current_anim_index]
        anim_control = self.leidian_model.getAnimControl(current_anim)
        
        if anim_control is None or not anim_control.isPlaying():
            self.current_anim_index = (self.current_anim_index + 1) % len(self.leidian_anims)
            next_anim = self.leidian_anims[self.current_anim_index]
            self.leidian_model.play(next_anim)
        
        return task.cont
    
    def _load_starfield(self):
        """加载星空"""
        try:
            # 天空球
            skydome = self.loader.loadModel(SKYDOME_MODEL_PATH)
            skydome.setScale(SKYDOME_SCALE)
            skydome.setTwoSided(True)
            skydome.setColor(*SKYDOME_COLOR)
            skydome.setBin(SKYDOME_BIN, 0)
            skydome.setDepthWrite(SKYDOME_DEPTHWRITE)
            skydome.setLightOff(SKYDOME_LIGHTOFF)
            skydome.reparentTo(self.render)
            
            # 星星
            self._create_stars()
        except Exception as e:
            print(f"星空加载失败: {e}")
    
    def _create_stars(self):
        """创建星星"""
        import random
        import math
        
        self.stars = self.render.attachNewNode(STAR_CONTAINER_NAME)
        self.stars.setBin(STAR_BIN, 1)
        self.stars.setDepthWrite(STAR_DEPTHWRITE)
        self.stars.setLightOff(STAR_LIGHTOFF)
        
        star_points = GeomNode(STAR_POINTS_NODE_NAME)
        star_points_np = self.stars.attachNewNode(star_points)
        
        vformat = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("stars", vformat, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        color = GeomVertexWriter(vdata, "color")
        
        for _ in range(STAR_NUM):
            theta = random.uniform(0, math.pi)
            phi = random.uniform(0, 2 * math.pi)
            r = SKYDOME_RADIUS
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            vertex.addData3f(x, y, z)
            
            brightness = random.uniform(0.7, 1.0)
            if random.random() < 0.8:
                rr, gg, bb = brightness, brightness, brightness
            else:
                rr, gg, bb = brightness, brightness * 0.8, brightness * 0.6
            color.addData4f(rr, gg, bb, 1.0)
        
        points = GeomPoints(Geom.UHStatic)
        points.addConsecutiveVertices(0, STAR_NUM)
        points.closePrimitive()
        geom = Geom(vdata)
        geom.addPrimitive(points)
        star_points.addGeom(geom)
        star_points_np.setAttrib(RenderModeAttrib.make(1))
        star_points_np.setRenderModeThickness(STAR_POINT_SIZE)
    
    # 游戏逻辑方法
    def switch_player(self):
        """切换玩家"""
        if self.current_player == PLAYER_WHITE:
            self.white_pieces_count -= 1
            self.current_player = PLAYER_BLACK
        else:
            self.black_pieces_count -= 1
            self.current_player = PLAYER_WHITE
    
    def update_gomoku_state(self, last_pos):
        """更新游戏状态"""
        row, col = last_pos // BOARD_SIZE, last_pos % BOARD_SIZE
        self.statistics.add_move(row, col, self.current_player)
        
        self.audio_manager.play_place_piece_sound()
        
        if self._handle_game_over():
            return
        
        self.switch_player()
        self._render_all_pieces()
        
        if self.is_ai_enabled and self.current_player == self.ai_side:
            self.ui_manager.show_ai_thinking()
            self.taskMgr.doMethodLater(0.1, self._delayed_ai_move, 'ai-move-task')
    
    def _delayed_ai_move(self, task):
        """延迟AI移动"""
        self.do_ai_move()
        return task.done
    
    def do_ai_move(self):
        """AI移动"""
        old_chessboard = copy.deepcopy(self.chessboard)
        self.chessboard = self.ai_player.get_next_chessboard(self.chessboard, self.ai_side)
        self.ui_manager.hide_ai_thinking()
        
        # 找到AI下的位置
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if old_chessboard.board[i][j] != self.chessboard.board[i][j]:
                    self.statistics.add_move(i, j, self.ai_side)
                    break
        
        self.audio_manager.play_place_piece_sound()
        self._render_all_pieces()
        
        if self._handle_game_over():
            return
        
        self.switch_player()
    
    def undo_move(self):
        """悔棋"""
        if self.game_over:
            print("Game is over, cannot undo")
            return
        
        if not self.statistics.can_undo():
            print("Cannot undo")
            return
        
        self.audio_manager.play_drag_piece_sound()
        
        steps_to_undo = 2 if self.is_ai_enabled and len(self.statistics.move_history) >= 2 else 1
        undone_moves = self.statistics.undo_moves(steps_to_undo)
        
        # 恢复棋盘状态
        for row, col, player in undone_moves:
            self.chessboard.board[row][col] = PIECE_EMPTY
            if player == PLAYER_WHITE:
                self.white_pieces_count += 1
            else:
                self.black_pieces_count += 1
        
        # 确定当前玩家
        if steps_to_undo == 2:
            self.current_player = PLAYER_WHITE if self.ai_side == PLAYER_BLACK else PLAYER_BLACK
        else:
            self.current_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
        
        self._render_all_pieces()
    
    def restart_game(self):
        """重新开始游戏"""
        print("Restarting game...")
        
        # 重置游戏状态
        self.chessboard = ChessBoard(size=BOARD_SIZE)
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.white_pieces_count = MAX_PIECES_PER_PLAYER
        self.black_pieces_count = MAX_PIECES_PER_PLAYER
        
        # 重置统计
        self.statistics.reset()
        
        # 清理UI和特效
        self.ui_manager.cleanup_game_over()
        self.effects_manager.cleanup_particles()
        
        # 重新渲染
        self._render_all_pieces()
        
        # 重新开始背景音乐
        self.audio_manager.play_current_bgm()
    
    def _handle_game_over(self):
        """处理游戏结束"""
        if not self.chessboard.check_winner():
            return False
        
        self.game_over = True
        winner = "Black" if self.chessboard.winner == PLAYER_BLACK else "White"
        
        # 创建特效
        winner_positions = self.chessboard.get_winner_positions()
        if winner_positions:
            self.effects_manager.create_victory_particles(winner_positions)
        
        self.ui_manager.hide_ai_thinking()
        self.audio_manager.stop_bgm()
        
        # 判断胜负
        is_ai_win = (winner == "White" and self.ai_side == PLAYER_WHITE) or \
                   (winner == "Black" and self.ai_side == PLAYER_BLACK)
        
        if is_ai_win:
            self.audio_manager.play_loser_sound()
        else:
            self.audio_manager.play_winner_sound()
        
        # 显示游戏结束界面
        final_stats = self.statistics.get_final_statistics()
        self.ui_manager.show_game_over(winner, is_ai_win, final_stats)
        
        return True
    
    def _render_all_pieces(self):
        """重新渲染所有棋子"""
        # 清理现有棋子
        for i in range(TOTAL_SQUARES):
            if self.pieces[i] is not None:
                self.pieces[i].obj.removeNode()
                self.pieces[i] = None
        
        # 重新创建棋子
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece_type = self.chessboard.get_stone(row, col)
                if piece_type != PIECE_EMPTY:
                    square_index = row * BOARD_SIZE + col
                    
                    if piece_type == PIECE_BLACK:
                        color = PIECEBLACK
                    elif piece_type == PIECE_WHITE:
                        color = WHITE_3D
                    else:
                        continue
                    
                    piece = Pawn(square_index, color, self)
                    piece.obj.setPos(square_pos(square_index))
                    self.pieces[square_index] = piece
    
    def check_winner(self):
        """检查胜利条件"""
        return self.chessboard.check_winner()