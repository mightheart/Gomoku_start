"""
常量定义文件
"""
# 设置常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 40

# 颜色定义 (2D游戏使用)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)  # 用于高亮获胜棋子

# 颜色定义 (3D游戏使用 - RGBA格式)
BLACK_3D = (0, 0, 0, 1)
WHITE_3D = (1, 1, 1, 1)
HIGHLIGHT = (0.92, 0.88, 0.77, 1)     # 高亮颜色
PIECEBLACK = (.15, .15, .15, 1)
WOOD_LIGHT = (0.92, 0.88, 0.77, 1)    # 浅色木材
WOOD_MEDIUM = (0.71, 0.55, 0.35, 1)   # 中等色调木材
WOOD_DARK = (0.54, 0.27, 0.07, 1)     # 深色木材
WOOD_WALNUT = (0.39, 0.26, 0.13, 1)   # 胡桃木色

# 游戏状态
GAME_STATE_MENU = "menu"
GAME_STATE_SELECT_SIZE = "select_size"  # 新增
GAME_STATE_SELECT_SIDE = "select_side"
GAME_STATE_PLAYING = "playing"

# 玩家标识
PLAYER_BLACK = 1
PLAYER_WHITE = 2

# 棋子符号
PIECE_BLACK = 'X'
PIECE_WHITE = 'O'
PIECE_EMPTY = ' '

# 摄像机控制常量
CAMERA_INITIAL_POSITION = (0, -16.5, 11)  # 初始摄像机位置
CAMERA_INITIAL_ANGLES = (0, -35, 0)     # 初始摄像机角度 (Roll-Pitch-Yaw)
CAMERA_ROTATION_SPEED = 30              # 视角旋转速度(度/秒)
CAMERA_MAX_PITCH = -15                  # 最大俯仰角
CAMERA_MIN_PITCH = -52                  # 最小俯仰角

# 摄像机加速度控制常量
CAMERA_ACCELERATION = 2000.0             # 加速度系数（度/秒²）
CAMERA_MAX_SPEED_MULTIPLIER = 10000.0       # 最大速度倍数
CAMERA_ACCELERATION_DELAY = 0.1      # 开始加速前的延迟时间（秒）

# 棋盘常量
BOARD_SIZE = 15                 # 棋盘大小 (15x15)
PIECE_DRAG_HEIGHT = 0.5         # 棋子拖动高度
TOTAL_SQUARES = 225             # 15x15
MAX_PIECES_PER_PLAYER = 100     # 15x15棋盘最多需要的棋子数

# 模型缩放比例
SQUARE_SCALE = 0.65  # 格子缩放比例
PIECE_SCALE = 0.85   # 棋子缩放比例
HIGHLIGHT_INDICATOR_RADIUS = 0.3  # 高亮指示器缩放比例
HIGHLIGHT_INDICATOR_SEGMENT = 32  # 高亮指示器分段数，越多越圆滑
MODEL_SCALE = 0.5  # 模型缩放比例，用于调节模型大小

# 棋盒位置
WHITE_BOX_POS = (0, -6, 0)  # 白棋盒位置
BLACK_BOX_POS = (0, 6, 0)   # 黑棋盒位置
BOX_SIZE = 1              # 棋盒缩放比例

# 背景图片位置常量
BACKGROUND_POSITION = (0, 100, 8)  # 默认位置，便于调整

# 装饰模型的轴向缩放比例
DECORATION_SCALE_X = 0.008  # X轴缩放比例
DECORATION_SCALE_Y = 0.008  # Y轴缩放比例
DECORATION_SCALE_Z = 0.008  # Z轴缩放比例

# 装饰模型的旋转和位置调节参数
DECORATION_ROTATION = (0, 90, 0)  # 默认旋转角度 (X, Y, Z)
DECORATION_POSITION_OFFSET = (0, 0, -0.3)  # 默认位置偏移 (X, Y, Z)

# 棋盘厚度模型的大小和位置调节参数
THICKNESS_SCALE = (0.5, 5.75, 0.2)  # 默认缩放比例 (X, Y, Z)
THICKNESS_POSITION_OFFSET = (0, 0, -0.21)  # 默认位置偏移 (X, Y, Z)

# 对手模型的路径、位置、缩放和旋转参数
OPPONENT_MODEL_PATH = "models/opponent1.obj"  # 对手模型路径
OPPONENT_MODEL_POSITION = (0,20,-10)  # 默认位置 (X, Y, Z)
OPPONENT_MODEL_SCALE = (15,15,15)  # 默认缩放比例 (X, Y, Z)
OPPONENT_MODEL_ROTATION = (0, 0, 0)  # 默认旋转角度 (X, Y, Z)

# 星空相关常量
SKYDOME_MODEL_PATH = "models/misc/sphere"
SKYDOME_SCALE = 1000
SKYDOME_COLOR = (0, 0, 0, 1)
SKYDOME_BIN = "background"
SKYDOME_DEPTHWRITE = False
SKYDOME_LIGHTOFF = 1
SKYDOME_RADIUS = 1000
STAR_CONTAINER_NAME = "stars"
STAR_BIN = "background"
STAR_DEPTHWRITE = False
STAR_LIGHTOFF = 1
STAR_POINTS_NODE_NAME = "star_points"
STAR_NUM = 3000
STAR_POINT_SIZE = 3.0
FALLBACK_SKY_FRAME = (-100, 100, -100, 100)
FALLBACK_SKY_P = -90
FALLBACK_SKY_Z = -50
FALLBACK_SKY_BIN = "background"
FALLBACK_SKY_DEPTHWRITE = False
FALLBACK_SKY_LIGHTOFF = 1

# 音频常量
SOUND_CLICK = "sound/place_piece.mp3"  # 落子
SOUND_DRAG = "sound/drag_piece.mp3"    # 提子
BGM_LIST = [ "sound/bgm3.mp3", 
            "sound/bgm2.wav", 
            "sound/bgm4.flac", "sound/bgm5.flac"]  # BGM列表
NAHITA_VOICE = [
                "sound/nahita/欢迎，终于来了.wav",
                "sound/nahita/欢迎，一起来下棋吗.wav",
                "sound/nahita/欢迎，请坐.wav",
                "sound/nahita/欢迎，等你好久了.wav",
                "sound/nahita/玩家失败，摸摸头.wav",
                "sound/nahita/玩家失败，你已经做的很好了.wav",
                "sound/nahita/玩家失败，换个策略吧.wav",
                "sound/nahita/玩家胜利，我迷路了.wav",
                "sound/nahita/玩家胜利，是我小瞧你了.wav",
                "sound/nahita/玩家胜利，变聪明啦.wav",
                "sound/nahita/思考，这不明智.wav",
                "sound/nahita/思考，让我想想.wav",
                "sound/nahita/思考，有趣.wav",
                "sound/nahita/思考，沉思.wav",
                "sound/nahita/思考，唔姆.wav",
                "sound/nahita/思考，下这好了.wav",
                "sound/nahita/玩家失败，又走神啦？.wav",
                "sound/nahita/思考，全部看见啦.wav",
                "sound/nahita/思考，这都被你发现了.wav",
                "sound/nahita/催促，又有心事吗？.wav",
                "sound/nahita/催促，头顶要长蘑菇了.wav",
                "sound/nahita/催促，长蘑菇2.wav",
                "sound/nahita/催促，长蘑菇3.wav",
                "sound/nahita/催促，想好下哪了吗.wav",
                "sound/nahita/催促，不知道干什么的话.......wav"
               ]
TINYUN_VOICE = [
                "sound/tinyun/催促，哎呀～方才是我失言，恩公不要往心里去啦.wav",
                "sound/tinyun/催促，哎呀都这个时辰了.wav",
                "sound/tinyun/催促，恩公别闪到腰了.wav",
                "sound/tinyun/催促，还得是小女子我.wav",
                "sound/tinyun/催促，我先活动活动手脚好了.wav",
                "sound/tinyun/欢迎，别小瞧我.wav",
                "sound/tinyun/欢迎，敢请问恩公大名？.wav",
                "sound/tinyun/欢迎，来下棋吗.wav",
                "sound/tinyun/思考，啊？.wav",
                "sound/tinyun/思考，恩公不必如此.wav",
                "sound/tinyun/思考，不错.wav",
                "sound/tinyun/思考，恩公明察.wav",
                "sound/tinyun/思考，麻烦啊.wav",
                "sound/tinyun/思考，哼哼.wav",
                "sound/tinyun/思考，唔....wav",
                "sound/tinyun/玩家胜利，恩公了不得.wav",
                "sound/tinyun/玩家胜利，给恩公烹上一桌好菜.wav",
                "sound/tinyun/玩家胜利，可以回去了吗.wav",
                "sound/tinyun/玩家胜利，小女子会继续努力.wav",
                "sound/tinyun/玩家胜利，这...我从不怀疑.wav",
                "sound/tinyun/玩家胜利，至少我进步了.wav",
                "sound/tinyun/玩家失败，恩公误会.wav",
                "sound/tinyun/玩家失败，承蒙关心.wav",
                "sound/tinyun/玩家失败，这算是恭维？.wav",
                "sound/tinyun/玩家失败，小女子不会乱嚼舌根.wav",
                "sound/tinyun/玩家失败，瞧瞧我的缜密心思.wav",
                ]
WINNER_MUSIC = "sound/winner_music.wav"  # 获胜音乐
LOSER_MUSIC = "sound/nahita/loser_music.wav"  # 失败音乐
SOUND_VOLUME = 0.18  # BGM默认音量

# 游戏统计和功能常量
MAX_UNDO_STEPS = 3                  # 最大悔棋次数
PLAYER_THINK_TIME_LIMIT = 30        # 玩家思考时间限制（秒）
STATISTICS_DISPLAY_TIME = 10        # 统计信息显示时间（秒）

# 特效常量
VICTORY_PARTICLE_COUNT = 100        # 胜利粒子数量
VICTORY_PARTICLE_DURATION = 3.0     # 胜利特效持续时间
FIREWORK_COLORS = [
    (1, 0.8, 0, 1),    # 金色
    (1, 0, 0, 1),      # 红色
    (0, 1, 0, 1),      # 绿色
    (0, 0, 1, 1),      # 蓝色
    (1, 0, 1, 1),      # 紫色
]

# UI常量
UI_TEXT_SCALE = 0.06
UI_TEXT_SCALE_SMALL = 0.05

# 统计信息位置（右上角）
UI_STATS_POS = (1.3, 0.85)

# 功能按钮位置（右侧中间）
UI_FUNCTION_POS_BASE = (1.25, 0.2)
UI_FUNCTION_SPACING = 0.12

# 当前玩家提示位置（屏幕上方中央）
UI_CURRENT_PLAYER_POS = (0, 0.9)

# 游戏结束文本位置
UI_GAME_OVER_POS = (0, 0)
UI_GAME_OVER_SCALE = 0.08

# UI颜色
UI_COLOR_WHITE = (1, 1, 1, 1)
UI_COLOR_YELLOW = (1, 1, 0, 1)
UI_COLOR_CYAN = (0, 1, 1, 1)
UI_COLOR_GREEN = (0, 1, 0, 1)
UI_COLOR_RED = (1, 0, 0, 1)
UI_COLOR_SHADOW = (0, 0, 0, 1)