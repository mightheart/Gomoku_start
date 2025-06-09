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
        # 标题
        self.title = OnscreenText(
            text="Gomoku Game",
            style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
            pos=(0.8, -0.95), scale=.07)
        
        # 控制提示
        controls = [
            ("ESC: Exit Gomoku", (0.06, -0.1)),
            ("Left Click & Drag: Grab & Release Piece", (0.06, -0.16)),
            ("A/D: rotate camera left/right (Triple click for auto)", (0.06, -0.22)),
            ("W/S: rotate camera up/down (Triple click for auto)", (0.06, -0.28)),
            ("SPACE: Stop auto rotation", (0.06, -0.34)),
            ("U: Undo move (max 3 times)", (0.06, -0.40)),
            ("Mouse Wheel: Zoom in/out", (0.06, -0.46)),
            ("R: Restart game", (0.06, -0.52))
        ]
        
        for text, pos in controls:
            element = OnscreenText(
                text=text, parent=self.base.a2dTopLeft,
                style=1, fg=(1, 1, 1, 1), pos=pos,
                align=TextNode.ALeft, scale=.05)
            self.hideable_ui_elements.append(element)
            element.hide()  # 初始隐藏
        
        # Tab提示
        self.tab_hint = OnscreenText(
            text="Press TAB to show controls and stats",
            parent=self.base.a2dBottomLeft, align=TextNode.ALeft,
            style=1, fg=(0.8, 0.8, 0.8, 1), pos=(0.06, 0.1), scale=.04)
    
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
    
    def update_current_player(self, current_player, is_ai_enabled, ai_side, game_over):
        """更新当前玩家显示"""
        if not self.function_ui['current_player'] or game_over:
            return
        
        player_name = "Black" if current_player == PLAYER_BLACK else "White"
        if is_ai_enabled and current_player == ai_side:
            player_name += " (AI)"
        self.function_ui['current_player'].setText(f"Current Player: {player_name}")
    
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
            victory_text = f"😔 Game Over! AI ({winner}) Wins!"
            text_color = UI_COLOR_RED
        else:
            victory_text = f"🎉 Congratulations! {winner} Wins!"
            text_color = UI_COLOR_GREEN
        
        combined_text = victory_text + "\n\n" + final_stats + "\n\nPress R to Restart"
        
        self.game_over_text = OnscreenText(
            text=combined_text, pos=UI_GAME_OVER_POS, scale=UI_GAME_OVER_SCALE,
            fg=text_color, shadow=UI_COLOR_SHADOW, align=TextNode.ACenter)
    
    def cleanup_game_over(self):
        """清理游戏结束UI"""
        if hasattr(self, 'game_over_text') and self.game_over_text:
            self.game_over_text.destroy()