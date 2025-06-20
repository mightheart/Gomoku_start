"""
主游戏逻辑 - 重构版本
"""
import time
import copy
import builtins
import random
import threading
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import WindowProperties, TextNode
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
from Gomoku_ai_minimax.ai import MinimaxAIPlayer
from Gomoku_ai_MCTS.aiv3 import MCTSAIPlayer

class Gomoku_Start(ShowBase):
    """五子棋游戏主类 - 重构版本"""
    
    def __init__(self, base, ai_type="classical", board_y=0, opponent_model_path=None, opponent_model_position=None):
        self.base = base
        for attr in dir(base):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(base, attr))
        
        # 存储AI类型、棋盘位置和默认对手模型
        self.ai_type = ai_type
        self.board_y = board_y
        self.opponent_model_path = opponent_model_path
        self.opponent_model_position = opponent_model_position

        # 鼠标光标重新显示
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        
        # 游戏状态 - 默认值，将在选择后设置
        self.current_player = None      # 将通过选择界面设置
        self.ai_side = None            # 将通过选择界面设置
        self.player_side = None        # 玩家选择的方
        self.white_pieces_count = MAX_PIECES_PER_PLAYER
        self.black_pieces_count = MAX_PIECES_PER_PLAYER
        self.is_ai_enabled = True
        self.game_over = False
        self.game_started = False      # 游戏是否已开始
        
        # 游戏组件
        self.chessboard = ChessBoard(size=BOARD_SIZE)
        
        # 根据AI类型创建AI实例
        self._create_ai_player()
        
        # 棋盘数据
        self.squares = [None for _ in range(TOTAL_SQUARES)]
        self.pieces = [None for _ in range(TOTAL_SQUARES)]
        
        # 选择界面
        self.side_selection_frame = None
        
        # 显示先后手选择界面
        self._show_side_selection()
    
    def _create_ai_player(self):
        if self.ai_type == "classical":
            self.ai_player = AIPlayer()
        elif self.ai_type == "minimax":
            self.ai_player = MinimaxAIPlayer()
        elif self.ai_type == "mcts":
            self.ai_player = MCTSAIPlayer()
        else:
            self.ai_player = AIPlayer()
    
    def _show_side_selection(self):
        """显示先后手选择界面"""
        # 创建选择界面背景
        self.side_selection_frame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-2, 2, -1.5, 1.5),
            pos=(0, 0, 0)
        )
        
        # 标题
        title_text = DirectLabel(
            text="Choose Your Side",
            text_scale=0.15,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 1.2),
            parent=self.side_selection_frame
        )
        
        # 说明文字
        desc_text = DirectLabel(
            text="Black goes first (Traditional rule)",
            text_scale=0.08,
            text_fg=(0.8, 0.8, 0.8, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.9),
            parent=self.side_selection_frame
        )
        
        # 选择黑棋按钮（先手）
        black_button = DirectButton(
            text="Play as BLACK\n(First Move)",
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.2, 0.2, 0.9),
            frameSize=(-0.7, 0.7, -0.3, 0.3),
            pos=(-0.8, 0, 0.3),
            command=self._select_side,
            extraArgs=[PLAYER_BLACK],
            parent=self.side_selection_frame
        )
        
        # 选择白棋按钮（后手）
        white_button = DirectButton(
            text="Play as WHITE\n(Second Move)",
            text_scale=0.06,
            text_fg=(0, 0, 0, 1),
            frameColor=(0.9, 0.9, 0.9, 0.9),
            frameSize=(-0.7, 0.7, -0.3, 0.3),
            pos=(0.8, 0, 0.3),
            command=self._select_side,
            extraArgs=[PLAYER_WHITE],
            parent=self.side_selection_frame
        )
        
        # 随机选择按钮
        random_button = DirectButton(
            text="Random Choice",
            text_scale=0.06,
            text_fg=(1, 1, 0, 1),
            frameColor=(0.5, 0.5, 0.5, 0.9),
            frameSize=(-1, 1, -0.3, 0.3),
            pos=(0, 0, -0.35),
            command=self._random_side_selection,
            parent=self.side_selection_frame
        )
        
        # 添加鼠标悬停效果 - 修复参数传递
        black_button.bind(DGG.ENTER, self._on_button_hover, 
                         extraArgs=[black_button, (0.3, 0.3, 0.3, 0.9)])
        black_button.bind(DGG.EXIT, self._on_button_unhover, 
                         extraArgs=[black_button, (0.2, 0.2, 0.2, 0.9)])
        
        white_button.bind(DGG.ENTER, self._on_button_hover, 
                         extraArgs=[white_button, (1, 1, 1, 0.9)])
        white_button.bind(DGG.EXIT, self._on_button_unhover, 
                         extraArgs=[white_button, (0.9, 0.9, 0.9, 0.9)])
        
        random_button.bind(DGG.ENTER, self._on_button_hover, 
                          extraArgs=[random_button, (0.6, 0.6, 0.6, 0.9)])
        random_button.bind(DGG.EXIT, self._on_button_unhover, 
                          extraArgs=[random_button, (0.5, 0.5, 0.5, 0.9)])
    
    def _on_button_hover(self, button, hover_color, event):
        """按钮悬停效果"""
        button['frameColor'] = hover_color  # 推荐用这种方式

    def _on_button_unhover(self, button, normal_color, event):
        """按钮取消悬停效果"""
        button['frameColor'] = normal_color
    
    def _random_side_selection(self):
        """随机选择先后手"""
        side = random.choice([PLAYER_BLACK, PLAYER_WHITE])
        side_name = "黑棋(先手)" if side == PLAYER_BLACK else "白棋(后手)"
        print(f"随机选择: {side_name}")
        self._select_side(side)
    
    def _select_side(self, player_side):
        """选择先后手"""
        self.player_side = player_side
        self.ai_side = PLAYER_WHITE if player_side == PLAYER_BLACK else PLAYER_BLACK
        
        # 设置开局玩家（黑棋先手）
        self.current_player = PLAYER_BLACK
        
        player_name = "黑棋(先手)" if player_side == PLAYER_BLACK else "白棋(后手)"
        ai_name = "白棋(后手)" if self.ai_side == PLAYER_WHITE else "黑棋(先手)"
        
        print(f"玩家选择: {player_name}")
        print(f"AI控制: {ai_name}")
        
        # 隐藏选择界面
        if self.side_selection_frame:
            self.side_selection_frame.destroy()
            self.side_selection_frame = None

        # 初始化游戏
        self._init_game()

        # 棋盒切换：如果玩家选黑棋，把黑棋盒和白棋盒位置对调
        if player_side == PLAYER_BLACK and hasattr(self, "board_setup"):
            # 交换棋盒和装饰的位置
            black_box = self.board_setup.black_box
            white_box = self.board_setup.white_box
            deco_black = self.board_setup.deco_black
            deco_white = self.board_setup.deco_white

            # 保存原始位置
            black_box_pos = black_box.getPos()
            white_box_pos = white_box.getPos()
            # 交换棋盒位置
            black_box.setPos(white_box_pos)
            white_box.setPos(black_box_pos)

            # 交换装饰位置（如果有）
            if deco_black and deco_white:
                deco_black_pos = deco_black.getPos()
                deco_white_pos = deco_white.getPos()
                deco_black.setPos(deco_white_pos)
                deco_white.setPos(deco_black_pos)

        # 如果AI先手，延迟让AI下棋
        if self.current_player == self.ai_side:
            print("AI先手，准备AI移动")
            self.taskMgr.doMethodLater(1.0, self._delayed_ai_move, 'ai-first-move')
    
    def _init_game(self):
        """初始化游戏"""
        # 初始化管理器
        self._init_managers()
        
        # 设置摄像机
        self._setup_camera(self.board_y)
        # self._setup_camera(board_y)
        # 初始化场景和棋盘外观
        self.scene_setup = SceneSetup(self.loader, self.render, self.taskMgr)
        self.scene_setup.setup_lighting()
        self.scene_setup.load_scene()

        self.board_setup = BoardSetup(
            self.loader, self.render,
            opponent_model_path=self.opponent_model_path,
            opponent_model_position=self.opponent_model_position
        )
        self.board_setup.setup_board()
        self.squares = self.board_setup.squares
        self.square_root = self.board_setup.square_root
        self.square_root.setY(self.board_y)
        # self.square_root.setY(board_y)

        # 创建高亮指示器需要在square_root创建完后再创建
        self.mouse_picker._create_highlight_indicator()

        # 执行任务
        self._start_tasks()
        
        # 标记游戏已开始
        self.game_started = True
        
        print("游戏初始化完成")
    
    def _init_managers(self):
        """初始化所有管理器"""
        self.audio_manager = AudioManager(self.loader, self.taskMgr)  # 初始化音频管理器
        self.audio_manager.set_ai_type(self.ai_type) # 向音頻管理器傳遞AI类型
        self.ui_manager = UIManager(self) # 初始化UI管理器
        self.statistics = GameStatistics(self.audio_manager) # 初始化游戏统计管理器
        self.effects_manager = EffectsManager(self.render, self.taskMgr) # 初始化特效管理器
        
        # 根据AI类型确定旋转中心
        rotation_center = self._get_rotation_center_by_ai_type(self.ai_type, self.board_y)
        
        # 创建控制器时传入旋转中心
        self.camera_controller = CameraController(rotation_center)
        self.mouse_picker = MousePicker(self)
        
        # 输入管理器需要在控制器创建后初始化
        self.input_manager = InputManager(self, self.camera_controller)
        
        # 设置引用
        self.mouse_picker.set_board_data(self.squares, self.pieces)
        self.mouse_picker.set_game_instance(self)
    
    def _get_rotation_center_by_ai_type(self, ai_type, board_y):
        """根据AI类型获取旋转中心"""
        if ai_type == "minimax":
            return (0, board_y, 0)
        elif ai_type == "mcts":
            return (0, board_y, 0)
        else:  # classical
            return (0, board_y, 0)
    
    def _setup_camera(self, board_y):
        """设置摄像机"""
        self.disableMouse()
        cam_x, cam_y, cam_z = CAMERA_INITIAL_POSITION
        cam_y += board_y
        self.camera.setPos(cam_x, cam_y - 4, cam_z)
        self.camera.setHpr(*CAMERA_INITIAL_ANGLES)
        self.camera.setP(self.camera.getP() + 10)
    
    def _start_tasks(self):
        """启动任务"""
        self.mouse_task = self.taskMgr.add(self._mouse_task, 'mouseTask')
        self.move_task = self.taskMgr.add(self._move_task, 'move')
    
    def _mouse_task(self, task):
        """鼠标任务"""
        if not self.game_started:
            return task.cont
        return self.mouse_picker.update(self.mouseWatcherNode, self.square_root)
    
    def _move_task(self, task):
        """主循环任务"""
        if not self.game_started:
            return task.cont
            
        dt = builtins.globalClock.getDt()
        self.camera_controller.update(dt)
        
        if not self.game_over:
            self.statistics.update_player_time(self.current_player, self.game_over)
            game_data = self.statistics.get_game_data()
            self.ui_manager.update_statistics(game_data)
            
            # 更新UI时传递player_side信息
            self.ui_manager.update_current_player(
                self.current_player, self.is_ai_enabled, 
                self.ai_side, self.game_over, self.player_side)
        
        return task.cont
    
    def _delayed_ai_move(self, task):
        """延迟AI移动"""
        threading.Thread(target=self.do_ai_move).start()
        return task.done
    
    # 其他游戏逻辑方法保持不变...
    def switch_player(self):
        """切换玩家"""
        old_player = self.current_player
        new_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
        
        # 先通知统计管理器切换（处理时间统计和AI语音）
        if hasattr(self, 'statistics'):
            self.statistics.switch_player(new_player)
        
        # 然后更新当前玩家
        self.current_player = new_player
        print(f"切换玩家: {old_player} -> {new_player}")
    
    def update_gomoku_state(self, last_pos):
        """更新游戏状态"""
        if not self.game_started:
            return
            
        row, col = last_pos // BOARD_SIZE, last_pos % BOARD_SIZE
        
        # 检查是否是玩家回合
        if self.current_player != self.player_side:
            print("不是玩家回合，无法下棋")
            return
        
        # 减少当前玩家的棋子数量
        if self.current_player == PLAYER_WHITE:
            self.white_pieces_count -= 1
        else:
            self.black_pieces_count -= 1
        
        self.statistics.add_move(row, col, self.current_player)
        self.audio_manager.play_place_piece_sound()
        
        self._render_all_pieces()

        if self._handle_game_over():
            return
        
        self.switch_player()  # 这里只负责切换，不减少棋子
        
        # 检查是否轮到AI
        if self.is_ai_enabled and self.current_player == self.ai_side:
            self.ui_manager.show_ai_thinking()
            self.taskMgr.doMethodLater(0.1, self._delayed_ai_move, 'ai-move-task')
    
    def do_ai_move(self):
        """AI移动"""
        if not self.game_started:
            return
            
        old_chessboard = copy.deepcopy(self.chessboard)
        self.chessboard = self.ai_player.get_next_chessboard(self.chessboard, self.ai_side)
        self.ui_manager.hide_ai_thinking()
        
        # 减少AI的棋子数量
        if self.ai_side == PLAYER_WHITE:
            self.white_pieces_count -= 1
        else:
            self.black_pieces_count -= 1
        
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
    
    def restart_game(self):
        """重新开始游戏"""
        print("Restarting game...")
        
        # 重置游戏状态
        self.chessboard = ChessBoard(size=BOARD_SIZE)
        self.current_player = PLAYER_BLACK  # 黑棋总是先手
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
    
        # 如果玩家是白棋，则AI先走
        if self.player_side == PLAYER_WHITE:
            self.taskMgr.doMethodLater(0.5, self._delayed_ai_move, 'ai-first-move')
    
    def undo_move(self):
        """悔棋"""
        if not self.game_started or self.game_over:
            print("Game is not started or over, cannot undo")
            return
        
        if not self.statistics.can_undo():
            print("Cannot undo")
            return
        
        # 播放悔棋音效
        self.audio_manager.play_drag_piece_sound()
        
        # 播放悔棋语音 - 传递AI类型
        self.statistics.play_undo_voice(ai_type=self.ai_type)
        
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
            self.current_player = self.player_side
        else:
            self.current_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
        
        self._render_all_pieces()
    
    def _back_to_csgo_mode(self):
        """返回CSGO漫游模式"""
        # 通知主控切换
        if hasattr(self, "messenger"):
            self.messenger.send("back-to-csgo")


    
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
        
        # 判断胜负（基于玩家选择的方）
        is_player_win = (winner == "White" and self.player_side == PLAYER_WHITE) or \
                       (winner == "Black" and self.player_side == PLAYER_BLACK)
        
        if is_player_win:
            self.audio_manager.play_ai_voice(identifier="玩家胜利", volume=1)
            self.audio_manager.play_winner_sound()
            print("玩家获胜！")
        else:
            self.audio_manager.play_ai_voice(identifier="玩家失败", volume=1)
            self.audio_manager.play_loser_sound()
            print("AI获胜！")
        
        # 显示游戏结束界面
        final_stats = self.statistics.get_final_statistics()
        self.ui_manager.show_game_over(winner, not is_player_win, final_stats)
        
        return True
    
    def _render_all_pieces(self):
        """重新渲染所有棋子"""
        if not self.game_started:
            return
            
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
                    # 关键：棋子obj要reparentTo(self.square_root)
                    piece.obj.reparentTo(self.square_root)
                    piece.obj.setPos(square_pos(square_index))
                    self.pieces[square_index] = piece
    
    def check_winner(self):
        """检查胜利条件"""
        return self.chessboard.check_winner()

    def cleanup(self):
        """清理所有资源"""
        # 清理选择界面
        if hasattr(self, "side_selection_frame") and self.side_selection_frame:
            self.side_selection_frame.destroy()
            self.side_selection_frame = None
            
        # 停止任务
        if hasattr(self, "mouse_task"):
            self.taskMgr.remove(self.mouse_task)
        if hasattr(self, "move_task"):
            self.taskMgr.remove(self.move_task)
            
        # 清理鼠标光标
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