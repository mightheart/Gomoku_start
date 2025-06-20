"""UI管理模块"""
import time
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from utils.constants import (
    UI_TEXT_SCALE, UI_TEXT_SCALE_SMALL, UI_STATS_POS, UI_CURRENT_PLAYER_POS,
    UI_GAME_OVER_POS, UI_GAME_OVER_SCALE, UI_COLOR_WHITE, UI_COLOR_YELLOW,
    UI_COLOR_GREEN, UI_COLOR_RED, UI_COLOR_SHADOW, MAX_UNDO_STEPS,
    PLAYER_BLACK, PLAYER_WHITE
)

class UIManager:
    """UI管理器"""
    
    def __init__(self, base_instance):
        self.base = base_instance
        self.function_ui = {}
        self.hideable_ui_elements = []
        self.ui_visible = False
        self.tab_hint = None
        self.ai_thinking_text = None
        self.game_over_text = None
        
        self._setup_control_ui()
        self._setup_function_ui()
        self._setup_ai_thinking_text()
    
    def _setup_control_ui(self):
        """设置控制提示UI"""
        try:
            # 标题
            self.title = OnscreenText(
                text="Gomoku Game",
                style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
                pos=(0.8, -0.95), scale=.07)
        except Exception as e:
            print(f"創建提示UI失敗: {e}")
            self.title = None
        
        # 控制提示
        controls = [
            ("ESC: Exit Gomoku", (0.06, -0.1)),
            ("Left Click & Drag: Grab & Release Piece", (0.06, -0.16)),
            ("A/D: rotate camera left/right (Triple click for auto)", (0.06, -0.22)),
            ("W/S: rotate camera up/down (Triple click for auto)", (0.06, -0.28)),
            ("SPACE: Stop auto rotation", (0.06, -0.34)),
            ("U: Undo move (max 3 times)", (0.06, -0.40)),
            ("Mouse Wheel: Zoom in/out", (0.06, -0.46)),
            ("R: Restart game", (0.06, -0.52)),
            ("B: Back to roam mode", (0.06, -0.58))
        ]
        
        for text, pos in controls:
            try:
                element = OnscreenText(
                    text=text, parent=self.base.a2dTopLeft,
                    style=1, fg=(1, 1, 1, 1), pos=pos,
                    align=TextNode.ALeft, scale=.05)
                self.hideable_ui_elements.append(element)
                element.hide()  # 初始隐藏
            except Exception as e:
                print(f"創建控制文本 '{text}' 失敗: {e}")

        # Tab提示 - 添加异常处理
        try:
            self.tab_hint = OnscreenText(
                text="Press TAB to show controls and stats",
                parent=self.base.a2dBottomLeft, align=TextNode.ALeft,
                style=1, fg=(0.8, 0.8, 0.8, 1), pos=(0.06, 0.1), scale=.04)
        except Exception as e:
            print(f"創建Tab菜單失敗: {e}")
            self.tab_hint = None
    
    def _setup_function_ui(self):
        """设置功能UI"""
        try:
            # 统计信息
            self.function_ui['stats_text'] = OnscreenText(
                text="", pos=UI_STATS_POS, scale=UI_TEXT_SCALE_SMALL,
                fg=UI_COLOR_WHITE, align=TextNode.ALeft)
            
            # 当前玩家
            self.function_ui['current_player'] = OnscreenText(
                text="", pos=UI_CURRENT_PLAYER_POS, scale=UI_TEXT_SCALE,
                fg=UI_COLOR_WHITE, align=TextNode.ACenter)
            
            # 初始隐藏
            self.function_ui['stats_text'].hide()
            
        except Exception as e:
            print(f"Failed to setup function UI: {e}")
            self.function_ui = {'stats_text': None, 'current_player': None}
    
    def _setup_ai_thinking_text(self):
        """设置AI思考提示"""
        self.ai_thinking_text = OnscreenText(
            text="AI Thinking...", parent=self.base.a2dTopRight,
            align=TextNode.ARight, style=1, fg=UI_COLOR_YELLOW,
            shadow=UI_COLOR_SHADOW, pos=(-0.06, -0.1), scale=UI_TEXT_SCALE)
        self.ai_thinking_text.hide()
    
    def toggle_ui_visibility(self):
        """切换UI显示状态"""
        self.ui_visible = not self.ui_visible
        
        for element in self.hideable_ui_elements:
            if element:
                element.show() if self.ui_visible else element.hide()
        
        for key, element in self.function_ui.items():
            if element and key != 'current_player':
                element.show() if self.ui_visible else element.hide()
        
        # 更新Tab提示
        if self.tab_hint:  # 先检查当前是否存在Tab菜单
            if self.ui_visible:
                self.tab_hint.setText("Press TAB to hide controls and stats")
            else:
                self.tab_hint.setText("Press TAB to show controls and stats")
    
    def update_statistics(self, game_data):
        """更新统计信息"""
        if not self.function_ui['stats_text']:
            return
        
        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        
        stats_text = f"Game Time: {format_time(game_data['game_duration'])}\n"
        stats_text += f"Moves: {game_data['move_count']}\n"
        stats_text += f"Black Time: {format_time(game_data['black_time'])}\n"
        stats_text += f"White Time: {format_time(game_data['white_time'])}\n"
        stats_text += f"Undo Left: {MAX_UNDO_STEPS - game_data['undo_count']}"
        
        self.function_ui['stats_text'].setText(stats_text)
    
    def update_current_player(self, current_player, is_ai_enabled, ai_side, game_over, player_side=None):
        """更新当前玩家显示（支持动态先后手）"""
        if game_over:
            return
        
        # 确定玩家控制的颜色
        if player_side:
            player_color = "Black" if player_side == PLAYER_BLACK else "White" 
            ai_color = "White" if player_side == PLAYER_BLACK else "Black"
        else:
            # 兼容旧版本
            player_color = "White"
            ai_color = "Black"
        
        if current_player == (player_side if player_side else PLAYER_WHITE):
            # 玩家回合
            current_text = f"Your Turn ({player_color})"
            color = (0, 1, 0, 1)  # 绿色
        else:
            # AI回合
            current_text = f"AI Turn ({ai_color})"  
            color = (1, 1, 0, 1)  # 黄色
        
        if hasattr(self, 'current_player_label'):
            self.current_player_label['text'] = current_text
            self.current_player_label['text_fg'] = color
    
    def show_ai_thinking(self):
        """显示AI思考状态"""
        if self.ai_thinking_text:
            self.ai_thinking_text.show()
    
    def hide_ai_thinking(self):
        """隐藏AI思考状态"""
        if self.ai_thinking_text:
            self.ai_thinking_text.hide()
    
    def show_game_over(self, winner, is_ai_win, final_stats):
        """显示游戏结束界面"""
        if is_ai_win:
            victory_text = f" Game Over! AI ({winner}) Wins!"
            text_color = UI_COLOR_RED
        else:
            victory_text = f" Congratulations! {winner} Wins!"
            text_color = UI_COLOR_GREEN
        
        combined_text = victory_text + "\n\n" + final_stats + "\nPress B to go back to the world" + "\nPress R to Restart"
        
        self.game_over_text = OnscreenText(
            text=combined_text, pos=UI_GAME_OVER_POS, scale=UI_GAME_OVER_SCALE,
            fg=text_color, shadow=UI_COLOR_SHADOW, align=TextNode.ACenter)
    
    def cleanup_game_over(self):
        """清理游戏结束UI"""
        if hasattr(self, 'game_over_text') and self.game_over_text:
            self.game_over_text.destroy()
    
    def cleanup(self):
        """彻底清理所有UI元素"""
        # 销毁所有 OnscreenText
        if hasattr(self, 'title') and self.title:
            self.title.destroy()
            self.title = None
        if hasattr(self, 'tab_hint') and self.tab_hint:
            self.tab_hint.destroy()
            self.tab_hint = None
        if hasattr(self, 'ai_thinking_text') and self.ai_thinking_text:
            self.ai_thinking_text.destroy()
            self.ai_thinking_text = None
        if hasattr(self, 'game_over_text') and self.game_over_text:
            self.game_over_text.destroy()
            self.game_over_text = None

        # 销毁功能UI
        if hasattr(self, 'function_ui'):
            for key, element in self.function_ui.items():
                if element:
                    element.destroy()
            self.function_ui.clear()

        # 销毁可隐藏UI
        if hasattr(self, 'hideable_ui_elements'):
            for element in self.hideable_ui_elements:
                if element:
                    element.destroy()
            self.hideable_ui_elements.clear()