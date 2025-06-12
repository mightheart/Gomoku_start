"""
主游戏逻辑 - 重构版本
"""
import time
import copy
import builtins
from direct.showbase.ShowBase import ShowBase

from panda3d.core import WindowProperties
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
from .setup_scene import SceneSetup
from .setup_board import BoardSetup
class Gomoku_Start(ShowBase):
    """五子棋游戏主类 - 重构版本"""
    
    def __init__(self,base):
        self.base=base
        for attr in dir(base):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(base, attr))
        
        #鼠标光标重新显示
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        
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
        
        # 初始化场景和棋盘外观
        self.scene_setup = SceneSetup(self.loader, self.render, self.taskMgr)
        self.scene_setup.setup_lighting()
        self.scene_setup.load_scene()

        self.board_setup = BoardSetup(self.loader, self.render)
        self.board_setup.setup_board()
        self.squares = self.board_setup.squares
        self.square_root=self.board_setup.square_root
        
        #执行任务
        self._start_tasks()
        
    
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
    
    def _back_to_csgo_mode(self):
        """返回CSGO漫游模式"""
        # 通知主控切换
        if hasattr(self, "messenger"):
            self.messenger.send("back-to-csgo")

    def restart_game(self):
        """重新开始游戏"""
        print("Restarting game...")
        
        # 重置游戏状态
        self.chessboard = ChessBoard(size=BOARD_SIZE)
        self.current_player = PLAYER_WHITE
        self.game_over = False
        self.white_pieces_count = MAX_PIECES_PER_PLAYER
        self.black_pieces_count = MAX_PIECES_PER_PLAYER
        
        # 重置统计
        self.statistics.reset()
        
        # 清理UI和特效
        self.ui_manager.cleanup_game_over()
        self.effects_manager.cleanup_particles()
        
        # 停止所有音乐
        self.audio_manager.stop_all_music()
        
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
            self.audio_manager.play_nahita_voice("摸摸头")
            self.audio_manager.play_loser_sound()
        else:
            self.audio_manager.play_nahita_voice("变聪明啦")
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

    def cleanup(self):
        """清理所有资源，便于模式切换"""
        # 停止任务
        if hasattr(self, "mouse_task"):
            self.taskMgr.remove(self.mouse_task)
        if hasattr(self, "move_task"):
            self.taskMgr.remove(self.move_task)
        #清理鼠标光标
        if hasattr(self, "mouse_picker"):
            self.mouse_picker.cleanup()
        # 清理UI和特效
        if hasattr(self, "ui_manager"):
            self.ui_manager.cleanup()
        if hasattr(self, "effects_manager"):
            self.effects_manager.cleanup_particles()
        # 清理场景和棋盘
        if hasattr(self, "scene_setup"):
            self.scene_setup.cleanup()
        if hasattr(self, "board_setup"):
            self.board_setup.cleanup()
        if hasattr(self, "pieces"):
            for piece in self.pieces:
                if piece is not None and hasattr(piece, "obj"):
                    piece.obj.removeNode()
            self.pieces = [None for _ in range(TOTAL_SQUARES)]
        # 清理音乐
        if hasattr(self, "audio_manager"):
            self.audio_manager.stop_all_music()
        # 其它需要清理的内容可按需补充