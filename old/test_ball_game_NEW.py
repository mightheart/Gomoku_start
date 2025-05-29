import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 40

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)  # 用于高亮获胜棋子


class GobangGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("五子棋游戏")
        self.clock = pygame.time.Clock()

        # 加载背景图片
        try:
            self.background_image = pygame.image.load("background.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background_image = None

        # 初始化字体
        try:
            self.font_large = pygame.font.SysFont("simhei", 48)
            self.font_medium = pygame.font.SysFont("simhei", 36)
            self.font_small = pygame.font.SysFont("simhei", 24)
        except:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)

        # 游戏状态
        self.game_state = "menu"  # menu, select_size, playing, game_over
        self.board_size = 15  # 默认棋盘大小
        self.board = []
        self.current_player = 1  # 1 = 黑子, 2 = 白子
        self.winner = 0
        self.winning_five = []  # 存储获胜的五子位置
        self.calculate_board_params()

    def calculate_board_params(self):
        """根据棋盘大小计算相关参数"""
        self.BOARD_WIDTH = self.board_size * CELL_SIZE
        self.BOARD_HEIGHT = self.board_size * CELL_SIZE
        self.BOARD_X = (SCREEN_WIDTH - self.BOARD_WIDTH) // 2
        self.BOARD_Y = 120

    def draw_background(self):
        """绘制背景"""
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            # 如果没有背景图片，使用渐变背景
            for y in range(SCREEN_HEIGHT):
                color_value = int(200 + 55 * (y / SCREEN_HEIGHT))
                color = (color_value, color_value - 20, color_value - 40)
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

    def reset_game(self):
        """重置游戏"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.winner = 0
        self.winning_five = []  # 重置获胜的五子信息
        self.game_state = "playing"

    def draw_menu(self):
        """绘制开始菜单"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_large.render("五子棋游戏", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 游戏说明
        rules = [
            "游戏规则：",
            "1. 黑白双方轮流下棋",
            "2. 先连成5子者获胜",
            "3. 可横、竖、斜连线",
            "",
            "点击任意位置开始游戏"
        ]

        y_offset = 250
        for rule in rules:
            if rule == "游戏规则：":
                text = self.font_medium.render(rule, True, RED)
            elif rule == "":
                y_offset += 10
                continue
            else:
                text = self.font_small.render(rule, True, BLACK)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40

    def draw_size_selection(self):
        """绘制棋盘大小选择界面"""
        self.draw_background()

        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(LIGHT_BROWN)
        self.screen.blit(overlay, (0, 0))

        # 标题
        title_text = self.font_medium.render("选择棋盘大小", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 棋盘大小选项
        sizes = ["15×15 (标准)", "13×13", "11×11"]
        size_buttons = []

        y_offset = 250
        for i, size in enumerate(sizes):
            # 绘制按钮
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset, 300, 60)
            pygame.draw.rect(self.screen, BLUE, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2, border_radius=10)

            # 绘制文字
            text = self.font_medium.render(size, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            # 保存按钮信息
            size_buttons.append((button_rect, i))
            y_offset += 120

        return size_buttons

    def draw_board(self):
        """绘制棋盘"""
        # 绘制棋盘背景
        board_rect = pygame.Rect(self.BOARD_X - 20, self.BOARD_Y - 20,
                                 self.BOARD_WIDTH + 40, self.BOARD_HEIGHT + 40)
        pygame.draw.rect(self.screen, BROWN, board_rect)

        # 绘制网格线
        for i in range(self.board_size):
            # 横线
            start_x = self.BOARD_X + 20
            end_x = self.BOARD_X + self.BOARD_WIDTH - CELL_SIZE + 20
            y = self.BOARD_Y + i * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, BLACK, (start_x, y), (end_x, y), 2)

            # 竖线
            start_y = self.BOARD_Y + 20
            end_y = self.BOARD_Y + self.BOARD_HEIGHT - CELL_SIZE + 20
            x = self.BOARD_X + i * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, BLACK, (x, start_y), (x, end_y), 2)

        # 绘制天元
        center = self.board_size // 2
        x = self.BOARD_X + center * CELL_SIZE + CELL_SIZE // 2
        y = self.BOARD_Y + center * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, BLACK, (x, y), 4)

    def draw_pieces(self):
        """绘制棋子，并高亮显示获胜的五子"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != 0:
                    x = self.BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
                    y = self.BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

                    # 检查是否是获胜的五子之一
                    is_winning = any(pos == (row, col) for pos in self.winning_five)

                    if self.board[row][col] == 1:  # 黑子
                        pygame.draw.circle(self.screen, BLACK, (x, y), 15)
                        pygame.draw.circle(self.screen, WHITE, (x, y), 15, 2)
                        if is_winning:
                            # 高亮显示获胜的黑子
                            pygame.draw.circle(self.screen, GOLD, (x, y), 18, 3)
                    else:  # 白子
                        pygame.draw.circle(self.screen, WHITE, (x, y), 15)
                        pygame.draw.circle(self.screen, BLACK, (x, y), 15, 2)
                        if is_winning:
                            # 高亮显示获胜的白子
                            pygame.draw.circle(self.screen, GOLD, (x, y), 18, 3)

    def draw_ui(self):
        """绘制游戏界面信息"""
        # 当前玩家提示
        if self.winner == 0:
            if self.current_player == 1:
                player_text = self.font_medium.render("当前: 黑方", True, BLACK)
            else:
                player_text = self.font_medium.render("当前: 白方", True, BLACK)
        else:
            if self.winner == 1:
                player_text = self.font_medium.render("黑方获胜！", True, RED)
            else:
                player_text = self.font_medium.render("白方获胜！", True, RED)

        self.screen.blit(player_text, (50, 10))

        # 重新开始按钮
        restart_text = self.font_small.render("按R键重新开始", True, GRAY)
        self.screen.blit(restart_text, (SCREEN_WIDTH - 200, 10))

        # 返回菜单按钮
        menu_text = self.font_small.render("按M键返回菜单", True, GRAY)
        self.screen.blit(menu_text, (SCREEN_WIDTH - 200, 40))

    def get_board_position(self, mouse_pos):
        """将鼠标位置转换为棋盘坐标"""
        x, y = mouse_pos

        # 检查是否在棋盘范围内
        if (self.BOARD_X <= x <= self.BOARD_X + self.BOARD_WIDTH and
                self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_HEIGHT):

            col = (x - self.BOARD_X) // CELL_SIZE
            row = (y - self.BOARD_Y) // CELL_SIZE

            # 确保在有效范围内
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                return row, col

        return None, None

    def place_piece(self, row, col):
        """放置棋子"""
        if self.board[row][col] == 0 and self.winner == 0:
            self.board[row][col] = self.current_player

            # 检查是否获胜
            if self.check_winner(row, col):
                self.winner = self.current_player
                # 找到获胜的五子
                self.find_winning_five(row, col)
            else:
                # 切换玩家
                self.current_player = 3 - self.current_player  # 1->2, 2->1

            return True
        return False

    def check_winner(self, row, col):
        """检查是否有玩家获胜"""
        player = self.board[row][col]
        directions = [
            (0, 1),  # 水平
            (1, 0),  # 垂直
            (1, 1),  # 主对角线
            (1, -1)  # 反对角线
        ]

        for dr, dc in directions:
            count = 1  # 包含当前棋子

            # 向一个方向检查
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                count += 1
                r += dr
                c += dc

            # 向相反方向检查
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True

        return False

    def find_winning_five(self, row, col):
        """找到获胜的五子位置"""
        player = self.board[row][col]
        directions = [
            (0, 1),  # 水平
            (1, 0),  # 垂直
            (1, 1),  # 主对角线
            (1, -1)  # 反对角线
        ]

        self.winning_five = []  # 清空之前的获胜五子

        for dr, dc in directions:
            # 存储当前方向上的连续棋子
            line_pieces = [(row, col)]

            # 向一个方向检查
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                line_pieces.append((r, c))
                r += dr
                c += dc

            # 向相反方向检查
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size and
                   self.board[r][c] == player):
                line_pieces.append((r, c))
                r -= dr
                c -= dc

            # 如果找到至少5个连续棋子
            if len(line_pieces) >= 5:
                # 按方向排序，确保是连续的
                if dr != 0 or dc != 0:
                    line_pieces.sort(key=lambda pos: (pos[0] * dr + pos[1] * dc,
                                                      (pos[1] * dc if dr == 0 else pos[0] * dr)))

                # 找到包含当前棋子的最长连续段
                start_index = None
                for i, (r, c) in enumerate(line_pieces):
                    if r == row and c == col:
                        start_index = i
                        break

                if start_index is not None:
                    # 获取连续的5个子
                    start = max(0, start_index - 4)
                    end = min(len(line_pieces), start_index + 5)
                    self.winning_five = line_pieces[start:end]

                    # 确保我们有连续的5个
                    if len(self.winning_five) > 5:
                        # 找到包含当前棋子的连续5子
                        for i in range(len(self.winning_five) - 4):
                            if any(pos == (row, col) for pos in self.winning_five[i:i + 5]):
                                self.winning_five = self.winning_five[i:i + 5]
                                return
                    elif len(self.winning_five) == 5:
                        return

    def handle_menu_events(self, event):
        """处理菜单事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.game_state = "select_size"

    def handle_size_selection_events(self, event):
        """处理棋盘大小选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            size_buttons = self.draw_size_selection()

            for button, size_idx in size_buttons:
                if button.collidepoint(mouse_pos):
                    # 设置棋盘大小
                    if size_idx == 0:
                        self.board_size = 15
                    elif size_idx == 1:
                        self.board_size = 13
                    else:  # size_idx == 2
                        self.board_size = 11

                    # 重新计算棋盘参数并重置游戏
                    self.calculate_board_params()
                    self.reset_game()
                    return

    def handle_game_events(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                row, col = self.get_board_position(event.pos)
                if row is not None and col is not None:
                    self.place_piece(row, col)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R键重新开始
                self.reset_game()
            elif event.key == pygame.K_m:  # M键返回菜单
                self.game_state = "menu"

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif self.game_state == "menu":
                    self.handle_menu_events(event)

                elif self.game_state == "select_size":
                    self.handle_size_selection_events(event)

                elif self.game_state == "playing":
                    self.handle_game_events(event)

            # 绘制
            if self.game_state == "menu":
                self.draw_menu()

            elif self.game_state == "select_size":
                self.draw_size_selection()

            elif self.game_state == "playing":
                self.draw_background()
                self.draw_board()
                self.draw_pieces()
                self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = GobangGame()
    game.run()


if __name__ == "__main__":
    main()
