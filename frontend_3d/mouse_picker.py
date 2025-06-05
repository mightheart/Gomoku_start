"""鼠标拾取功能模块"""

from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, BitMask32
from panda3d.core import LineSegs
from direct.task.Task import Task
from utils.constants import HIGHLIGHT, PIECE_DRAG_HEIGHT, WHITE_3D, PIECEBLACK, TOTAL_SQUARES, HIGHLIGHT_INDICATOR_RADIUS, HIGHLIGHT_INDICATOR_SEGMENT, BOARD_SIZE
from utils.helpers import square_color, point_at_z, square_pos, _get_piece_name
from pieces.chess_pieces import Pawn

class MousePicker:
    """鼠标拾取器"""
    
    def __init__(self, base_instance):
        # 直接使用 ShowBase 实例
        self.base = base_instance
        self.camera = base_instance.camera
        self.render = base_instance.render
        
        # 设置碰撞系统
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        self.picker_node.setFromCollideMask(BitMask32.bit(1))
        
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker.addCollider(self.picker_np, self.pq)
        
        # 创建高亮指示器
        self._create_highlight_indicator()

        # 状态变量
        self.hi_sq = False
        # self.dragging = False
        self.squares = None
        self.pieces = None
        # 五子棋相关状态
        self.temp_piece = None
        self.dragging_new_piece = False
        self.game_instance = None  # 用于访问游戏状态
    
    def _create_highlight_indicator(self):
        """创建圆形高亮指示器"""
        # 使用LineSegs创建一个圆形
        lines = LineSegs()
        lines.setThickness(3.0)
        lines.setColor(HIGHLIGHT[0], HIGHLIGHT[1], HIGHLIGHT[2], HIGHLIGHT[3])  # 使用高亮颜色
        
        import math
        radius = HIGHLIGHT_INDICATOR_RADIUS  # 指示器半径，与棋子大小相近
        segments = HIGHLIGHT_INDICATOR_SEGMENT  # 圆形分段数，越多越圆滑
        
        # 绘制圆形
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            if i == 0:
                lines.moveTo(x, y, 0)
            else:
                lines.drawTo(x, y, 0)
        
        # 创建节点
        self.highlight_circle = self.render.attachNewNode(lines.create())
        self.highlight_circle.hide()  # 初始隐藏

    def set_board_data(self, squares, pieces):
        """设置棋盘数据引用"""
        self.squares = squares
        self.pieces = pieces

    def set_game_instance(self, game_instance):
        """设置游戏实例引用"""
        self.game_instance = game_instance

    def _can_create_piece(self, box_type):
        """检查是否可以创建新棋子"""
        if not self.game_instance:
            return False
            
        if box_type == 'white':
            return (self.game_instance.current_player == 'white' and 
                    self.game_instance.white_pieces_count > 0)
        elif box_type == 'black':
            return (self.game_instance.current_player == 'black' and 
                    self.game_instance.black_pieces_count > 0)
        return False

    def _create_new_piece_from_box(self, box_type):
        """从棋盒创建新棋子"""
        if not self._can_create_piece(box_type):
            print(f"无法创建 {box_type} 棋子 - 不是当前玩家或棋子用完")
            return
            
        # 创建临时棋子跟随鼠标
        color = WHITE_3D if box_type == 'white' else PIECEBLACK
        self.temp_piece = Pawn(-1, color, self.base)  # -1表示临时位置
        self.dragging_new_piece = True
        print(f"从{box_type}棋盒创建新棋子")

    def _is_valid_gomoku_placement(self):
        """检查五子棋放置位置是否有效"""
        # 检查是否有选中的格子
        if self.hi_sq is False or self.hi_sq < 0 or self.hi_sq >= TOTAL_SQUARES:
            return False
        
        # 检查位置是否已被占用
        if self.pieces[self.hi_sq] is not None:
            print(f"位置 {self._get_square_name(self.hi_sq)} 已被占用")
            return False
        
        return True

    def _place_new_gomoku_piece(self):
        """放置新的五子棋棋子"""
        if not self.temp_piece:
            return
            
        # 将临时棋子放置到棋盘
        self.pieces[self.hi_sq] = self.temp_piece
        self.temp_piece.square = self.hi_sq
        self.temp_piece.obj.setPos(square_pos(self.hi_sq))
        
        # 更新游戏状态
        if self.game_instance:
            self.game_instance._update_gomoku_state(self.hi_sq)
        
        piece_color = "白" if self.temp_piece.obj.getColor()[0] > 0.5 else "黑"
        print(f"{piece_color}棋子放置在 {self._get_square_name(self.hi_sq)}")
        
        # 清理临时状态
        self.temp_piece = None

    def _cancel_new_piece(self):
        """取消新棋子放置"""
        if self.temp_piece:
            self.temp_piece.obj.removeNode()
            self.temp_piece = None
            print("取消棋子放置")
    
    def update(self, mouse_watcher_node, square_root):
        """更新鼠标拾取(每帧调用)"""
        # 清除当前高亮
        if self.hi_sq is not False:
            self.highlight_circle.hide()
            self.hi_sq = False
        
        if not mouse_watcher_node.hasMouse():
            return Task.cont
            
        mpos = mouse_watcher_node.getMouse()
        
        # 设置射线
        self.picker_ray.setFromLens(self.base.camNode, mpos.getX(), mpos.getY())
        
        # 删除处理拖拽已有棋子的逻辑
        # if self.dragging is not False:
        #     near_point = self.render.getRelativePoint(self.camera, self.picker_ray.getOrigin())
        #     near_vec = self.render.getRelativeVector(self.camera, self.picker_ray.getDirection())
        #     self.pieces[self.dragging].obj.setPos(point_at_z(PIECE_DRAG_HEIGHT, near_point, near_vec))
        
        # 只处理拖拽新创建的棋子
        if self.dragging_new_piece and self.temp_piece:
            near_point = self.render.getRelativePoint(self.camera, self.picker_ray.getOrigin())
            near_vec = self.render.getRelativeVector(self.camera, self.picker_ray.getDirection())
            self.temp_piece.obj.setPos(point_at_z(PIECE_DRAG_HEIGHT, near_point, near_vec))
        
        # 碰撞检测 - 检测整个场景
        self.picker.traverse(self.render)
        if self.pq.getNumEntries() > 0:
            self.pq.sortEntries()
            entry = self.pq.getEntry(0)
            hit_node = entry.getIntoNode()
            
            # 检查是否点击了棋盒
            if hit_node.hasTag('piece_box'):
                box_type = hit_node.getTag('piece_box')
                # 棋盒不需要高亮显示，但需要记录这个状态
                self.hi_sq = -1  # 用特殊值表示棋盒
                return Task.cont
            
            # 检查是否点击了棋盘格子
            if hit_node.hasTag('square'):
                i = int(hit_node.getTag('square'))
                
                # 只有空位才显示高亮（防止点击已有棋子时的混淆）
                if self.pieces[i] is None:
                    # 显示圆形高亮指示器在选中的格子上
                    square_position = square_pos(i)
                    self.highlight_circle.setPos(square_position.x, square_position.y, square_position.z + 0.02)
                    self.highlight_circle.show()
                    self.hi_sq = i
        
        return Task.cont
    
    def grab_piece(self):
        """从棋盒创建新棋子（取消移动已有棋子功能）"""
        print(f"grab_piece 被调用，hi_sq = {self.hi_sq}, 碰撞条目数 = {self.pq.getNumEntries()}")
        
        # 只检查棋盒点击，不再处理棋盘上的棋子
        if self.pq.getNumEntries() > 0:
            hit_node = self.pq.getEntry(0).getIntoNode()
            
            # 只处理棋盒点击
            if hit_node.hasTag('piece_box'):
                box_type = hit_node.getTag('piece_box')
                print(f"点击了{box_type}棋盒")
                self._create_new_piece_from_box(box_type)
                return
            elif hit_node.hasTag('square'):
                print("棋盘上的棋子无法移动")  # 提示用户
                return
            else:
                print("点击了未知对象")
        
        # 删除原来移动棋子的逻辑
        # if self.hi_sq is not False and self.hi_sq >= 0 and self.pieces[self.hi_sq]:
        #     self.dragging = self.hi_sq
        #     self.hi_sq = False
        #     from utils.helpers import _get_piece_name
        #     print(f"抓取棋子: {_get_piece_name(self.pieces[self.dragging])}")
    
    def release_piece(self):
        """释放棋子（只处理新创建的棋子）"""
        # 只处理新棋子放置
        if self.dragging_new_piece:
            if self._is_valid_gomoku_placement():
                self._place_new_gomoku_piece()
            else:
                self._cancel_new_piece()
            self.dragging_new_piece = False
            return
        
        # 原来移动已有棋子的逻辑
        # if self.dragging is not False:
        #     if self.hi_sq is False:
        #         # 回到原位置
        #         self.pieces[self.dragging].obj.setPos(square_pos(self.dragging))
        #         print(f"棋子回到原位置: {self._get_square_name(self.dragging)}")
        #     else:
        #         # 检查目标位置是否为空（五子棋规则：只能放在空位）
        #         if self.pieces[self.hi_sq] is None:
        #             # 移动棋子
        #             piece_name = self._get_piece_name(self.pieces[self.dragging])
        #             from_square = self._get_square_name(self.dragging)
        #             to_square = self._get_square_name(self.hi_sq)
        #             
        #             print(f"棋子移动: {piece_name} 从 {from_square} 到 {to_square}")
        #             self._swap_pieces(self.dragging, self.hi_sq)
        #         else:
        #             # 位置被占用，回到原位
        #             self.pieces[self.dragging].obj.setPos(square_pos(self.dragging))
        #             print(f"目标位置被占用，棋子回到原位置: {self._get_square_name(self.dragging)}")
        #     
        #     self.dragging = False
    
    def _get_square_name(self, square_index):
        """将数字索引转换为五子棋坐标 - 15x15"""
        if square_index < 0 or square_index >= TOTAL_SQUARES:
            return "无效位置"
        
        row = square_index // BOARD_SIZE  # 行 (0-14)
        col = square_index % BOARD_SIZE   # 列 (0-14)
        
        return f"({col + 1},{row + 1})"  # 返回格式如 (1,1), (2,3) 等，从1开始计数

    # 交换已有棋子的逻辑
    # def _swap_pieces(self, fr, to):
    #     """交换两个棋子的位置"""
    #     temp = self.pieces[fr]
    #     self.pieces[fr] = self.pieces[to]
    #     self.pieces[to] = temp
        
    #     if self.pieces[fr]:
    #         self.pieces[fr].square = fr
    #         self.pieces[fr].obj.setPos(square_pos(fr))
    #     if self.pieces[to]:
    #         self.pieces[to].square = to
    #         self.pieces[to].obj.setPos(square_pos(to))

    def _get_piece_name(self, piece):
        """获取棋子名称"""
        if not piece:
            return "空"
        
        piece_type = piece.__class__.__name__
        color = "白" if piece.obj.getColor()[0] > 0.5 else "黑"  # 简单的颜色判断
        
        piece_names = {
            'Pawn': '兵',
            'King': '王',
            'Queen': '后',
            'Bishop': '象',
            'Knight': '马',
            'Rook': '车'
        }
        
        return f"{color}{piece_names.get(piece_type, piece_type)}"

    def place_ai_piece(self, square_index, ai_chr):
        """AI自动在指定格子落子"""
        if self.pieces[square_index] is not None:
            print(f"AI落子失败，位置{square_index}已被占用")
            return
        color = WHITE_3D if ai_chr == 'O' else PIECEBLACK
        piece = Pawn(square_index, color, self.base)
        self.pieces[square_index] = piece
        piece.square = square_index
        piece.obj.setPos(square_pos(square_index))
        if self.game_instance:
            self.game_instance._update_gomoku_state(square_index)
        print(f"AI落子: {'白' if ai_chr == 'O' else '黑'}棋子放在{self._get_square_name(square_index)}")